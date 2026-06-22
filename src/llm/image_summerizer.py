import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import io
import asyncio

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

def generate_caption(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    inputs = processor(image, return_tensors="pt")
    out = model.generate(**inputs)
    return processor.decode(out[0], skip_special_tokens=True)

async def get_image_summary(image_bytes):
    loop = asyncio.get_event_loop()
    try:
        summary = await loop.run_in_executor(None, generate_caption, image_bytes)
        return {"summary": summary, "products": []}
    except:
        return {"summary": "", "products": []}
