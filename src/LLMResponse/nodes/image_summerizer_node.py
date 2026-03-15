from utils.asyncHandler import asyncHandler
from src.LLMResponse.entity import State
from src.LLMResponse.utils.main_utils import load_image
from src.LLMResponse.llm.image_summerizer import get_image_summary

@asyncHandler
async def image_summerizer_node(state: State):
    if state.image_path:
        image_bytes = await load_image(state.image_path)
        res = await get_image_summary(image_bytes)
        state.image_summary = res.get("summary", "")
    return state