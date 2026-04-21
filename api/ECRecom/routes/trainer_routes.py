from fastapi import APIRouter
from pydantic import BaseModel
from src.ECRecom.pipelines.training_pipeline import TrainingPipeline
from src.ECRecom.entity.config_entity import DataIngestionConfig, DataTransformationConfig
import logging
router = APIRouter()


async def run_pipeline():
    try:
        logging.info("Initializing Data Ingestion and Transformation Configs...")
        data_ingestion_config = DataIngestionConfig()
        data_transformation_config = DataTransformationConfig()
        
        logging.info("Initializing Training Pipeline...")
        training_pipeline = TrainingPipeline(
            data_ingestion_config=data_ingestion_config,
            data_transformation_config=data_transformation_config
        )
        
        logging.info("Starting Pipeline Execution...")
        artifact = await training_pipeline.initiate()
        logging.info(f"Pipeline completed successfully. Artifact: {artifact}")
        print(f"Pipeline completed. Artifact: {artifact}")
    except Exception as e:
        logging.error(f"Error running pipeline: {e}")
        print(f"Error running pipeline: {e}")

@router.get("/")
async def train_model():
    try:
        await run_pipeline()
        return {
            "status": "success"
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
