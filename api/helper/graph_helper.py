import os
import shutil
from src.constants import PUBLIC_TEMP_DIR
import logging
import asyncio

from src.graphs.builder import deleteThread as GraphThreadDeletor

async def delete_thread(thread_id: str, delay_seconds: int):
    """Utility function to delete a thread after a specific delay."""
    if delay_seconds > 0:
        logging.info(f"Waiting {delay_seconds} seconds before deleting thread: {thread_id}")
        await asyncio.sleep(delay_seconds)

    logging.info(f"Starting deletion of thread data for thread_id: {thread_id}")
    
    try:
        path = os.path.join(PUBLIC_TEMP_DIR, thread_id)
        
        if os.path.exists(path):
            shutil.rmtree(path,ignore_errors=True)
            logging.info(f"Deleted public data for path: {path}")
        else:
            logging.info(f"No public data found for path: {path}")    
        try:   
            logging.info(f"Starting deletion of memory data for thread_id: {thread_id}") 
            GraphThreadDeletor(thread_id)
            logging.info(f"Deleted memory data for thread_id: {thread_id}")
        except Exception as e:
            logging.error(f"Error during graph thread deletion for thread_id {thread_id}: {e}")    
        logging.info(f"Completed deletion of thread data for thread_id: {thread_id}")
    except Exception as e:
        logging.error(f"Error deleting thread data for thread_id {thread_id}: {e}")