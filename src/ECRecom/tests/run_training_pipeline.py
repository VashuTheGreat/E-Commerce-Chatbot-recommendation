import os
import sys

# Ensure root directory is in path before imports
sys.path.append(os.getcwd())

import asyncio
import logging
from logger import * # Import specificly if needed or just use logging
from src.ECRecom.pipelines.training_pipeline import TrainingPipeline
from src.ECRecom.entity.config_entity import DataIngestionConfig, DataTransformationConfig

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

if __name__ == "__main__":
    async def main():
        await run_pipeline()
    
    asyncio.run(main())