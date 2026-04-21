from huggingface_hub.utils import logging
import asyncio
import os
import sys

sys.path.append(os.getcwd())

from logger import *
import logging

from src.LLMResponse.pipelines.prediction_pipeline import run_llm_response_pipeline


async def test_normal_chat():
    logging.info("=" * 60)
    logging.info("TEST 1 — Normal chat (no images)")
    logging.info("=" * 60)

    result = await run_llm_response_pipeline(
        user_query="Hello! What kind of products do you have?",
        thread_id="test_chat_1"
    )




    logging.info("TEST 1 — Result received")

    logging.info(f"Test 1 result ",result)
    print("\n--- TEST 1: Normal Chat ---")
    print(f"Final Response:\n{result.get('final_response')}")
    print(f"DB Results: {result.get('db_results')}")


async def test_image_recommendation():
    logging.info("=" * 60)
    logging.info("TEST 2 — Image upload + recommendation request")
    logging.info("=" * 60)

    image_paths = []
    test_img = "./tempImage/test1.png"
    if os.path.exists(test_img):
        image_paths = [test_img]
        logging.info(f"Found test image at: {test_img}")
    else:
        logging.warning(f"No test image found at {test_img} — running without images")

    result = await run_llm_response_pipeline(
        user_query="I uploaded a product image. Please recommend similar products.",
        thread_id="test_image_1",
        image_paths=image_paths
    )

    logging.info("TEST 2 — Result received")
    logging.info(f"TEST 2 result {result}")
    print("\n--- TEST 2: Image + Recommendation ---")
    print(f"Final Response:\n{result.get('final_response')}")
    print(f"\nDB Results ({len(result.get('db_results', []))} items):")
    for i, item in enumerate(result.get("db_results", []), 1):
        print(f"  {i}. {item}")


async def test_direct_recommendation():
    logging.info("=" * 60)
    logging.info("TEST 3 — Direct recommendation request (no images)")
    logging.info("=" * 60)

    result = await run_llm_response_pipeline(
        user_query="Show me some men's casual navy blue shirts.",
        thread_id="test_rec_1"
    )

    logging.info("TEST 3 — Result received")
    logging.info(f"TEST 3 result {result}")
    print("\n--- TEST 3: Direct Recommendation (no image) ---")
    print(f"Final Response:\n{result.get('final_response')}")
    print(f"\nDB Results ({len(result.get('db_results', []))} items):")
    for i, item in enumerate(result.get("db_results", []), 1):
        print(f"  {i}. {item}")


async def main():
    logging.info("run_pipeline — starting all test scenarios")
    await test_normal_chat()
    await test_direct_recommendation()
    await test_image_recommendation()
    logging.info("run_pipeline — all tests completed")


if __name__ == "__main__":
    asyncio.run(main())
