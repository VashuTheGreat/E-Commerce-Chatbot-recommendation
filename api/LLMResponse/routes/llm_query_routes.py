import fastapi
from fastapi import UploadFile, APIRouter, BackgroundTasks
import os
import aiofiles
import uuid
import shutil
import asyncio
from src.LLMResponse.pipelines.prediction_pipeline import run_llm_response_pipeline
import logging
router = APIRouter()

async def cleanup_temp_dir(path: str):
    await asyncio.sleep(300)
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            os.makedirs("tempImage",exist_ok=True)
            logging.info(f"cleaned folder {path}")
        except:
            logging.info(f"Error while cleaning folder {path}")
            pass

@router.post("/response")
async def llm_response(file: UploadFile, query: str, background_tasks: BackgroundTasks):
    try:
        thread_id = str(uuid.uuid4())
        temp_dir = os.path.abspath("./tempImage")
        os.makedirs(temp_dir, exist_ok=True)
        file_path = os.path.join(temp_dir, f"{thread_id}.jpg")
        
        async with aiofiles.open(file_path, "wb") as out_file:
            content = await file.read()
            await out_file.write(content)
        
        result = await run_llm_response_pipeline(query, thread_id)
        
        background_tasks.add_task(cleanup_temp_dir, temp_dir)
        
        return {
            "status": "success",
            "thread_id": thread_id,
            "image_summary": result.get("image_summary"),
            "llm_query": result.get("llm_query")
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
