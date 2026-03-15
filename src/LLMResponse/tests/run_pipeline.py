import asyncio
import os
import sys
sys.path.append(os.getcwd())
from logger import *
import logging

from src.LLMResponse.pipelines.prediction_pipeline import run_llm_response_pipeline

async def main():
    thread_id = "test1"
    user_query = "show me some similar products"
    result = await run_llm_response_pipeline(user_query, thread_id)
    logging.info(result)
    print(f"Summary: {result.get('image_summary')}")
    print(f"Query: {result.get('llm_query')}")

if __name__ == "__main__":
    asyncio.run(main())
