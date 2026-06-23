import os
import logging
from typing import List

import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader

from src.utils.asyncHandler import asyncHandler
from src.retreiver.custom_vec_db import CustomVectorDb
from src.entity.data_access import Connect_data
import requests
from src.entity.model import MyModel
from src.entity.config_entity import ModelTrainingConfig, DataIngestionConfig
from io import BytesIO


class InferenceDataSet(Dataset):

    def __init__(self, config, data_path=None, data_frame=None):
        self.config = config
        if data_frame is not None:
            self.data_frame = data_frame
        elif data_path is not None:
            self.data_frame = pd.read_csv(data_path)
        else:
            raise ValueError("Either data_path or data_frame must be provided")

    def __len__(self):
        return len(self.data_frame)

    def __getitem__(self, idx):

        item = self.data_frame.iloc[idx]

        img_url = item["image_url"]

        try:
            response = requests.get(img_url)
            response.raise_for_status()
        except Exception:
            response = requests.get(img_url)

        img_path = BytesIO(response.content)

        text_data = str(item["product_search_description"])

        import numpy as np
        import torch

        # Process image to tensor and extract features
        image = Image.open(img_path).convert("RGB")
        image_np = np.array(image)
        image_tensor = self.config.transforms(image_np).unsqueeze(0).to(self.config.device)

        with torch.no_grad():
            img_feat = self.config.image_encoder(image_tensor).squeeze(0).cpu()

        # Process text to tokens and extract features
        tokens = self.config.tokenizer(
            text_data,
            padding="max_length",
            truncation=True,
            max_length=self.config.config.max_len,
            return_tensors="pt"
        ).to(self.config.device)

        with torch.no_grad():
            txt_feat = self.config.text_encoder(tokens['input_ids'], tokens['attention_mask']).squeeze(0).cpu()

        return (
            img_feat,
            txt_feat,
            item.to_dict()
        )


class Vectorizer:

    def __init__(self, data_path=None):

        if data_path is None:
            data_path = DataIngestionConfig().data_path
        self.data_path = data_path

        self.config = ModelTrainingConfig()

        self.model = MyModel(
            config=self.config
        )

        try:
            import dagshub
            dagshub.auth.add_app_token(os.getenv("MLFLOW_API"))
            dagshub.init(repo_owner='vanshsharma7832', repo_name='E-Commerce-Chatbot-recommendation', mlflow=True)
        except Exception as ex:
            logging.warning(f"DagsHub initialization in Vectorizer failed: {ex}")

        import torch
        from src.models.muti_model import ImageEncoder, TextEncoder
        from transformers import AutoTokenizer
        from torchvision.transforms import v2

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
        self.image_encoder = ImageEncoder(self.config).to(self.device).eval()
        self.text_encoder = TextEncoder(self.config).to(self.device).eval()

        self.transforms = v2.Compose([
            v2.ToImage(),
            v2.ToDtype(torch.float32, scale=True),
            v2.Resize(size=(224, 224), antialias=True),
            v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        import mlflow.pytorch
        self.model.model = mlflow.pytorch.load_model(
            model_uri="models:/E-Commerce-Recommendation_Model/1",
            map_location=self.device
        )

        self.vec_db = CustomVectorDb(
            api_key=os.getenv("PINECONE_API_KEY"),
            index_name="multimodal-search",
            dimension=self.config.final_feature_output
        )

    @asyncHandler
    async def ingest_vec(self, override: bool = False):
        if override:
            print("DELETING ALL VECTORS FROM INDEX", flush=True)
            logging.warning("DELETING ALL VECTORS FROM INDEX")
            self.vec_db.delete_all()

        connector = Connect_data(data_path=self.data_path)
        df = await connector.load_data()
        if not override:
            existing_ids = set(self.vec_db.get_all_ids())

            df = df[~df["id"].astype(str).isin(existing_ids)]
        if df.empty:
            print("Data Already exist please overrde True for overide", flush=True)
            logging.warning("Data Already exist please overrde True for overide")
            return
        dataset = InferenceDataSet(
            data_frame=df,
            config=self
        )

        dataloader = DataLoader(
            dataset,
            batch_size=self.config.batch_size,
            shuffle=False
        )

        self.vec_db.batch_upsert(
            dataloader=dataloader,
            model=self.model
        )

    @asyncHandler
    async def get_similar_data(self, vector: List[float], top_k: int = 5):
        return self.vec_db.search(vector, top_k)
