import aiofiles

async def load_image(image_path: str) -> bytes:
    async with aiofiles.open(image_path, mode='rb') as f:
        return await f.read()
