from utils.asyncHandler import asyncHandler
from components.vectorizing_data import Vectorizer
import logging

class PredictionPipeline:
    def __init__(self):
        self.vectorizer=Vectorizer()
        logging.info("PredictionPipeline initialized.")
    @asyncHandler
    async def initiate(self,vector,k=5):
        logging.info("Starting Prediction Pipeline...")

        retreived_docs=await self.vectorizer.get_similar_data(
            vector=vector,
            top_k=k
        )
        logging.info("Prediction Pipeline completed successfully.")
        return retreived_docs
