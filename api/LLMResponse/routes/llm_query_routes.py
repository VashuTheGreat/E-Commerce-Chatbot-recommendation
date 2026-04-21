from fastapi import UploadFile, APIRouter, BackgroundTasks, File, Form
import os
import aiofiles
import uuid
import shutil
import asyncio
import time
from typing import Optional
from src.LLMResponse.pipelines.prediction_pipeline import run_llm_response_pipeline
import logging
from src.LLMResponse.memmory import memory

from api.constants import SECONDS  # e.g. SECONDS = 20
import logging
router = APIRouter()

# track last activity time of each thread
thread_last_activity = {}

# ------------------ CLEANUP FILES ------------------
async def cleanup_temp_dir(path: str):
    await asyncio.sleep(SECONDS)

    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            logging.info(f"cleaned folder {path}")
        except Exception as e:
            logging.error(f"Error while cleaning folder {path}: {e}")



async def deleteThread(thread_id: str):
    try:
        cp = memory
        # Check if thread exists first
        state = await cp.aget_tuple(config={'configurable': {'thread_id': thread_id}})
        if state is None:
            logging.info(f"Thread {thread_id} not found, nothing to delete.")
            return False
            
        await cp.adelete_thread(thread_id=thread_id)
        logging.info(f"Thread {thread_id} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting thread {thread_id}: {e}")
        return False
# ------------------ CLEANUP MEMORY ------------------
async def cleanup_temp_thread(thread_id: str):
    await asyncio.sleep(SECONDS)

    last_time = thread_last_activity.get(thread_id)

    if last_time and (time.time() - last_time) >= SECONDS:
        try:
            logging.info(f"Cleaning chats for thread_id {thread_id}")

            if await deleteThread(thread_id):
                thread_last_activity.pop(thread_id, None)
            else:
                logging.info(f"Thread {thread_id} not found, nothing to delete.")    

            logging.info(f"Cleaned chats for thread_id {thread_id}")

        except Exception as e:
            logging.error(f"Error while cleaning thread_id {thread_id}: {e}")


# ------------------ API ------------------
@router.post("/response")
async def llm_response(
    background_tasks: BackgroundTasks,
    query: str = Form(...),
    thread_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    try:
        if not thread_id:
            thread_id = str(uuid.uuid4())

        thread_last_activity[thread_id] = time.time()

        image_paths = []

        temp_dir = os.path.abspath(f"./tempImage/{thread_id}")
        os.makedirs(temp_dir, exist_ok=True)

        if file and file.filename:
            file_path = os.path.join(temp_dir, file.filename)

            async with aiofiles.open(file_path, "wb") as out_file:
                content = await file.read()
                await out_file.write(content)

            image_paths.append(file_path)

            background_tasks.add_task(cleanup_temp_dir, temp_dir)

        background_tasks.add_task(cleanup_temp_thread, thread_id)

        result = await run_llm_response_pipeline(
            user_query=query,
            thread_id=thread_id,
            image_paths=image_paths if image_paths else None
        )

        return {
            "status": "success",
            "thread_id": thread_id,
            "final_response": result.get("final_response"),
            "db_results": result.get("db_results", [])
        }

    except Exception as e:
        logging.error(f"API error: {e}")
        return {"status": "error", "message": str(e)}