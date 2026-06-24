import os
import logging
from typing import List
import pandas as pd

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from src.models.muti_model import ImageEncoder, TextEncoder
from transformers import AutoTokenizer
from torchvision.transforms import v2
import mlflow.pytorch
import torch
from src.utils.asyncHandler import asyncHandler
from src.retreiver.custom_vec_db import CustomVectorDb
from src.entity.data_access import Connect_data
import requests
from src.entity.model import MyModel
from src.entity.config_entity import ModelTrainingConfig, DataIngestionConfig
from io import BytesIO
from src.config.app_config import app_config
from src.constants import TEXT_MODEL_NAME, MODEL_URI

class InferenceDataSet(Dataset):
    def __init__(self, config, data_path=None, data_frame=None):
        logging.info(f"InferenceDataSet - initializing with config: {config}, data_path: {data_path}")
        self.config = config
        if data_frame is not None:
            logging.info("InferenceDataSet - using provided data_frame")
            self.data_frame = data_frame
        elif data_path is not None:
            logging.info(f"InferenceDataSet - loading data from csv path: {data_path}")
            self.data_frame = pd.read_csv(data_path)
        else:
            logging.error("InferenceDataSet - initialization failed: no data_path or data_frame provided")
            raise ValueError("Either data_path or data_frame must be provided")
        logging.info(f"InferenceDataSet - loaded data count: {len(self.data_frame)}")

    def __len__(self):
        length = len(self.data_frame)
        logging.info(f"InferenceDataSet - checking length: {length}")
        return length

    def __getitem__(self, idx):
        logging.info(f"InferenceDataSet - fetching item at index: {idx}")
        item = self.data_frame.iloc[idx]
        img_url = item["image_url"]
        logging.info(f"InferenceDataSet - downloading image url: {img_url}")
        try:
            response = requests.get(img_url)
            response.raise_for_status()
        except Exception as e:
            logging.warning(f"InferenceDataSet - primary download failed for url {img_url}: {e}. retrying...")
            response = requests.get(img_url)
        img_path = BytesIO(response.content)
        text_data = str(item["product_search_description"])
        image = Image.open(img_path).convert("RGB")
        image_np = np.array(image)
        image_tensor = self.config.transforms(image_np).unsqueeze(0).to(self.config.device)
        logging.info(f"InferenceDataSet - image processed to tensor shape: {image_tensor.shape}")
        with torch.no_grad():
            img_feat = self.config.image_encoder(image_tensor).squeeze(0).cpu()
        tokens = self.config.tokenizer(
            text_data,
            padding="max_length",
            truncation=True,
            max_length=self.config.config.max_len,
            return_tensors="pt"
        ).to(self.config.device)
        logging.info(f"InferenceDataSet - text tokenized. tokens shape: {tokens['input_ids'].shape}")
        with torch.no_grad():
            txt_feat = self.config.text_encoder(tokens['input_ids'], tokens['attention_mask']).squeeze(0).cpu()
        logging.info(f"InferenceDataSet - extraction complete for item index {idx}")
        return (
            img_feat,
            txt_feat,
            item.to_dict()
        )

class Vectorizer:
    def __init__(self, data_path=None):
        logging.info(f"Vectorizer - initializing with data_path: {data_path}")
        if data_path is None:
            data_path = DataIngestionConfig().data_path
        self.data_path = data_path
        self.config = ModelTrainingConfig()
        logging.info("Vectorizer - instantiating model wrapper")
        self.model = MyModel(config=self.config)
        try:
            logging.info("Vectorizer - initializing DagsHub/MLflow logging integration")
            import dagshub
            dagshub.auth.add_app_token(app_config.mlflow_api_key)
            dagshub.init(repo_owner=app_config.dagshub_owner, repo_name=app_config.dagshub_repo, mlflow=True)
            logging.info("Vectorizer - DagsHub MLflow integration ready")
        except Exception as ex:
            logging.warning(f"Vectorizer - DagsHub initialization failed: {ex}")
        
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logging.info(f"Vectorizer - using device: {self.device}")
        self.tokenizer = AutoTokenizer.from_pretrained(TEXT_MODEL_NAME, token=app_config.huggingface_api_key)
        self.image_encoder = ImageEncoder(self.config).to(self.device).eval()
        self.text_encoder = TextEncoder(self.config).to(self.device).eval()
        self.transforms = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Resize(size=(224, 224), antialias=True),
            v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        logging.info("Vectorizer - loading model checkpoints from MLflow registry")
        self.model.model = mlflow.pytorch.load_model(
            model_uri=MODEL_URI,
            map_location=self.device
        )
        logging.info("Vectorizer - MLflow model loaded successfully. connecting to Pinecone.")
        self.vec_db = CustomVectorDb(
            api_key=app_config.pine_cone_api_key,
            index_name="multimodal-search",
            dimension=self.config.final_feature_output
        )
        logging.info("Vectorizer - Pinecone client and index initialized")

    @asyncHandler
    async def ingest_vec(self, override: bool = False):
        logging.info(f"Vectorizer.ingest_vec - initiating ingestion. override: {override}")
        if override:
            logging.warning("Vectorizer.ingest_vec - deleting existing vectors from Pinecone index")
            self.vec_db.delete_all()
        connector = Connect_data(data_path=self.data_path)
        df = await connector.load_data()
        if not override:
            logging.info("Vectorizer.ingest_vec - retrieving existing vector IDs from Pinecone")
            existing_ids = set(self.vec_db.get_all_ids())
            logging.info(f"Vectorizer.ingest_vec - retrieved {len(existing_ids)} existing IDs")
            df = df[~df["id"].astype(str).isin(existing_ids)]
        if df.empty:
            logging.warning("Vectorizer.ingest_vec - all data already exists in vector store. skipping ingestion.")
            return
        logging.info(f"Vectorizer.ingest_vec - processing dataset for {len(df)} samples")
        dataset = InferenceDataSet(
            data_frame=df,
            config=self
        )
        dataloader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=False
        )
        logging.info("Vectorizer.ingest_vec - starting batch upsert into Pinecone")
        self.vec_db.batch_upsert(
            dataloader=dataloader,
            model=self.model
        )
        logging.info("Vectorizer.ingest_vec - ingestion completed successfully")

    @asyncHandler
    async def get_similar_data(self, vector: List[float], top_k: int = 5):
        logging.info(f"Vectorizer.get_similar_data - querying Pinecone vector store for top_k: {top_k}")
        res = self.vec_db.search(vector, top_k)
        logging.info(f"Vectorizer.get_similar_data - search complete. response type: {type(res)}")
        return res
