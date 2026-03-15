from utils.asyncHandler import asyncHandler
from src.ECRecom.entity.config_entity import DataIngestionConfig,DataTransformationConfig
from src.ECRecom.components.data_ingestion import Data_Ingestor
from src.ECRecom.components.data_transformation import Data_Transformator
from src.ECRecom.entity.artifact_entity import TrainingPipelineArtifact
import logging

class TrainingPipeline:
    def __init__(self,data_ingestion_config:DataIngestionConfig,data_transformation_config:DataTransformationConfig):
        self.data_ingestion_config=data_ingestion_config
        self.data_transformation_config=data_transformation_config
        logging.info("TrainingPipeline initialized.")

    @asyncHandler
    async def initiate(self)->TrainingPipelineArtifact:
        logging.info("Starting Training Pipeline...")
        
        data_ingestor=Data_Ingestor(
            data_ingestion_config=self.data_ingestion_config
        )
        data_ingestion_artifact=await data_ingestor.initiate()
        
        data_transformator=Data_Transformator(
            data_ingestion_artifact=data_ingestion_artifact,
            data_transformation_config=self.data_transformation_config
        )
        data_transformation_artifact=await data_transformator.initiate()

        training_pipeline_artifact=TrainingPipelineArtifact(
            vector_db_path=data_transformation_artifact.vector_db_path
        )
        logging.info("Training Pipeline completed successfully.")
        return training_pipeline_artifact