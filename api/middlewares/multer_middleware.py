import shutil
import os
import logging
from fastapi import UploadFile,Request
from src.constants import PUBLIC_TEMP_DIR

os.makedirs(PUBLIC_TEMP_DIR, exist_ok=True)

async def multer_middleware(request: Request, file: UploadFile = None) -> str:
    logging.info(f"multer_middleware - entered with upload_file: {file}")
    thread_id = request.cookies.get("thread_id")
    if not file or not file.filename:
        logging.info("multer_middleware - no file was uploaded. returning empty path.")
        return ""
    file_path = os.path.join(PUBLIC_TEMP_DIR, thread_id, file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    logging.info(f"multer_middleware - uploading file to destination: {file_path}")
    with open(file_path, "wb") as f:
        logging.info(f"multer_middleware - copying uploaded stream into file: {file_path}")
        shutil.copyfileobj(file.file, f)
    logging.info(f"multer_middleware - file copy completed successfully. file_path: {file_path}")
    return file_path