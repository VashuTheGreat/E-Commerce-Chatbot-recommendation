from utils.asyncHandler import asyncHandler
from src.ECRecom.data_access.connect_data import Connect_data
from src.ECRecom.entity.config_entity import DataIngestionConfig
from src.ECRecom.constants import ARTIFACT_FOLDER
from src.ECRecom.entity.artifact_entity import DataIngestionArtifact
import pandas as pd
import os
import logging

class Data_Ingestor:
    def __init__(self,data_ingestion_config:DataIngestionConfig):
        self.data_ingestion_config=data_ingestion_config
        self.data_access=Connect_data(data_path=data_ingestion_config.data_path)
        logging.info(f"Data_Ingestor initialized with config: {data_ingestion_config}")
        

    @asyncHandler
    async def initiate(self)->DataIngestionArtifact:
        logging.info("Starting data ingestion...")
        data:pd.DataFrame=await self.data_access.load_data()
        logging.info(f"Data loaded successfully. Shape: {data.shape}")

        os.makedirs(ARTIFACT_FOLDER,exist_ok=True)
        artifact_dir = os.path.join(ARTIFACT_FOLDER,self.data_ingestion_config.data_artifact_folder_name)
        os.makedirs(artifact_dir,exist_ok=True)

        file_path=os.path.join(artifact_dir,self.data_ingestion_config.data_artifact_file_name)

        data.to_csv(file_path, index=False)
        logging.info(f"Data saved to artifact: {file_path}")

        data_ingestion_artifact = DataIngestionArtifact(
            data_saved_path=file_path
        )
        return data_ingestion_artifact
