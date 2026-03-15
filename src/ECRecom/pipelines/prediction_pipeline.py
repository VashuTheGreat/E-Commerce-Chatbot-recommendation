from utils.asyncHandler import asyncHandler
from src.ECRecom.components.similarity_fetch import Predict_similar
import logging

class PredictionPipeline:
    def __init__(self):
        self.predict_similar=Predict_similar()
        logging.info("PredictionPipeline initialized.")    
    @asyncHandler
    async def initiate(self,query:str,k=5):
        logging.info("Starting Prediction Pipeline...")
        
        retreived_docs=self.predict_similar.initiate(
            query=query,
            k=k
        )
        logging.info("Prediction Pipeline completed successfully.")
        return retreived_docs