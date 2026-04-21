
from exception import MyException

import sys



from src.LLMResponse.utils.main_utils import load_image
from src.LLMResponse.llm.image_summerizer import get_image_summary

async def analyse_image(image_path:str)->dict:
    try:
        image_bytes = await load_image(image_path)
        res = await get_image_summary(image_bytes)
        image_summary = res.get("summary", "")
        return image_summary

    except Exception as e:
        raise MyException(e,sys)    