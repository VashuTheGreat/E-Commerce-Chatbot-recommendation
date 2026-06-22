from src.utils.asyncHandler import asyncHandler
from src.entity.data_access import Connect_data
from src.entity.config_entity import DataIngestionConfig,DataTransformationConfig
from src.constants import ARTIFACT_FOLDER,BATCH_SIZE,EMBEDDING_MODEL,VECTOR_DB_PATH
from src.entity.artifact_entity import DataIngestionArtifact,DataTransformationArtifact
import pandas as pd
from pathlib import Path
import os
import logging
import requests
from concurrent.futures import ThreadPoolExecutor
import threading
import numpy as np

class Data_Transformator:
    def __init__(self,data_ingestion_artifact:DataIngestionArtifact,data_transformation_config:DataTransformationConfig):
        self.data_ingestion_artifact=data_ingestion_artifact
        self.data_transformation_config=data_transformation_config
        logging.info(f"Data_Transformator initialized.")

    @asyncHandler
    async def Save_images(self,df:pd.DataFrame):
        BASE_PATH = self.data_transformation_config.image_download_dir
        downloaded = 0
        failed = 0
        total_files = df.shape[0]
        os.makedirs(BASE_PATH,exist_ok=True)
        lock = threading.Lock()

        def save_images(row):
            nonlocal downloaded, failed
            image_id = row["id"]
            p = os.path.join(BASE_PATH, f"{image_id}.png")
            print(f"\rDownloaded: {downloaded}/{total_files} | Failed: {failed}/{total_files}", end="")
            if os.path.exists(p):
                with lock:
                    downloaded += 1
                return
            try:
                image_url = row["image_url"]
                r = requests.get(image_url, timeout=10)
                r.raise_for_status()
                with open(p, "wb") as f:
                    f.write(r.content)
                with lock:
                    downloaded += 1
            except Exception as e:
                logging.error(f"Failed to download image: {image_url}")
                with lock:
                    failed += 1

        with ThreadPoolExecutor(max_workers=10) as executor:
            list(executor.map(save_images, [row for _, row in df.iterrows()]))
        df['image_path']=[os.path.join(BASE_PATH,f"{img_id}.png") for img_id in df['id']]

    @asyncHandler
    async def initiate(self)->DataTransformationArtifact:
        logging.info("Initiating data transformation...")
        df = pd.read_csv(self.data_ingestion_artifact.data_saved_path)
        df.dropna(inplace=True)
        await self.Save_images(df)
        df_positive = df[['image_path', 'product_search_description']].copy()
        df_positive['label'] = 1.0
        df_negative = df[['image_path']].copy()
        df_negative['product_search_description'] = np.roll(df['product_search_description'].values, shift=1)
        df_negative['label'] = 0.0
        train_df = pd.concat([df_positive, df_negative], ignore_index=True)
        train_df = train_df.sample(frac=1,random_state=self.data_transformation_config.random_state).reset_index(drop=True)
        os.makedirs(self.data_transformation_config.transformed_artifact_dir,exist_ok=True)
        ratio = self.data_transformation_config.test_and_val_split
        split_val = ratio / 100.0 if ratio > 1.0 else ratio
        test_size_1 = split_val / 2.0
        test_size_2 = test_size_1 / (1.0 - test_size_1)

        from sklearn.model_selection import train_test_split
        train_val_df, test_df = train_test_split(
            train_df,
            test_size=test_size_1,
            random_state=self.data_transformation_config.random_state,
            stratify=train_df['label']
        )
        train_df_final, val_df = train_test_split(
            train_val_df,
            test_size=test_size_2,
            random_state=self.data_transformation_config.random_state,
            stratify=train_val_df['label']
        )

        train_path = os.path.join(self.data_transformation_config.transformed_artifact_dir, self.data_transformation_config.train_file_name)
        test_path = os.path.join(self.data_transformation_config.transformed_artifact_dir, self.data_transformation_config.test_file_name)
        val_path = os.path.join(self.data_transformation_config.transformed_artifact_dir, self.data_transformation_config.val_file_name)

        train_df_final.to_csv(train_path, index=False)
        test_df.to_csv(test_path, index=False)
        val_df.to_csv(val_path, index=False)

        data_transformation_artifact = DataTransformationArtifact(
            train_path=train_path,
            test_path=test_path,
            val_path=val_path,
            images_path=self.data_transformation_config.image_download_dir
        )
        return data_transformation_artifact
    