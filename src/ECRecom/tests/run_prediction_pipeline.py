import os
import sys

# Ensure root directory is in path before imports
sys.path.append(os.getcwd())

import asyncio
import logging
from logger import * # Import specificly if needed or just use logging
from src.ECRecom.pipelines.prediction_pipeline import PredictionPipeline

async def run_pipeline():
    try:
        query="""
        men apparel topwear shirts navy blue fall casual turtle check men navy blue shirt
        """
        logging.info("Initializing Prediction Pipeline...")
        
        logging.info("Initializing Prediction Pipeline...")
        prediction_pipeline = PredictionPipeline()
        
        
        logging.info("Starting Pipeline Execution...")
        retreived_docs = await prediction_pipeline.initiate(query=query,k=5)
        logging.info(f"Pipeline completed successfully. Artifact: {retreived_docs}")
        print(f"Pipeline completed. Artifact: {retreived_docs}")
    except Exception as e:
        logging.error(f"Error running pipeline: {e}")
        print(f"Error running pipeline: {e}")

if __name__ == "__main__":
    async def main():
        await run_pipeline()
    
    asyncio.run(main())