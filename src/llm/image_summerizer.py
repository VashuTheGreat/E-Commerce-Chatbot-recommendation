import torch
import logging
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import asyncio
from src.config.app_config import app_config

logging.info("loading BLIP image captioning processor and model")
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", token=app_config.huggingface_api_key)
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base", token=app_config.huggingface_api_key)
logging.info("BLIP processor and model loaded successfully")

def generate_caption(image_bytes):
    logging.info("generate_caption - opening image bytes")
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    logging.info("generate_caption - processing image with BLIP processor")
    inputs = processor(image, return_tensors="pt")
    logging.info("generate_caption - generating caption logits")
    out = model.generate(**inputs)
    caption = processor.decode(out[0], skip_special_tokens=True)
    logging.info(f"generate_caption - caption generation complete: '{caption}'")
    return caption

async def get_image_summary(image_bytes):
    logging.info(f"get_image_summary - starting async executor, bytes length: {len(image_bytes)}")
    loop = asyncio.get_event_loop()
    try:
        summary = await loop.run_in_executor(None, generate_caption, image_bytes)
        logging.info(f"get_image_summary - succeeded with caption: '{summary}'")
        return {"summary": summary, "products": []}
    except Exception as e:
        logging.error(f"get_image_summary - failed caption generation: {e}")
        return {"summary": "", "products": []}
