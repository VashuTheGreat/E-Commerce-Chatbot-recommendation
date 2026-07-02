import logging
import asyncio
import aiofiles
from PIL import Image
from transformers import BlipForConditionalGeneration, BlipProcessor
from src.utils.asyncHandler import asyncHandler
from src.constants import IMAGE_ANALYSIS_MODEL_NAME

# Conditional captioning prefix — guides BLIP to describe product attributes
BLIP_CAPTION_PREFIX = "a product image showing"


@asyncHandler
async def load_image(image_path: str) -> bytes:
    async with aiofiles.open(image_path, mode='rb') as f:
        return await f.read()


def _run_blip(image_path: str) -> str:
    """Synchronous BLIP inference — called via run_in_executor to avoid blocking."""
    logging.info(f"_run_blip - loading BLIP model: {IMAGE_ANALYSIS_MODEL_NAME}")

    processor = BlipProcessor.from_pretrained(IMAGE_ANALYSIS_MODEL_NAME)
    model = BlipForConditionalGeneration.from_pretrained(
        IMAGE_ANALYSIS_MODEL_NAME,
        low_cpu_mem_usage=True,
    )
    logging.info("_run_blip - model and processor loaded")

    image = Image.open(image_path).convert("RGB")
    logging.info(f"_run_blip - image opened: size={image.size}")

    # Conditional captioning: prefix tells BLIP what to focus on
    inputs = processor(image, text=BLIP_CAPTION_PREFIX, return_tensors="pt")
    logging.info("_run_blip - running conditional captioning generation")

    generated_ids = model.generate(
        **inputs,
        max_new_tokens=200,
        num_beams=4,
        early_stopping=True,
    )

    caption = processor.decode(generated_ids[0], skip_special_tokens=True)
    logging.info(f"_run_blip - caption generated (len={len(caption)}): {caption}")
    return caption


@asyncHandler
async def analyse_image(image_path: str) -> str:
    logging.info(f"analyse_image - starting BLIP analysis for: {image_path}")
    loop = asyncio.get_event_loop()
    caption = await loop.run_in_executor(None, _run_blip, image_path)
    logging.info(f"analyse_image - complete. caption length={len(caption)}")
    return caption
