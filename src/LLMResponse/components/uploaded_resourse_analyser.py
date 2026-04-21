import logging
import sys
from exception import MyException
from src.LLMResponse.utils.analyse_image import analyse_image
from src.LLMResponse.llm.llm_loader import llm
from src.LLMResponse.models.resource_analyser_model import ProductModels
from src.LLMResponse.prompts import PRODUCT_ANALYSIS_PROMPT
from langchain_core.messages import HumanMessage


class ResourceAnalyserComponent:
    def __init__(self):
        logging.info("ResourceAnalyserComponent initialised")

    async def analyse(self, content_path: str) -> ProductModels:
        logging.info(f"ResourceAnalyserComponent.analyse — processing path: {content_path}")

        try:
            content_ext = content_path.split(".")[-1].lower()
            logging.debug(f"Detected file extension: {content_ext}")

            if content_ext in ("jpg", "jpeg", "png", "webp"):
                content_type = "image"
            elif content_ext == "pdf":
                content_type = "pdf"
            else:
                content_type = "unsupported"

            logging.info(f"Resolved content_type: {content_type}")

            match content_type:
                case "image":
                    logging.info(f"Analysing image at: {content_path}")
                    caption: str = await analyse_image(content_path)
                    logging.debug(f"BLIP caption received: {caption}")

                    prompt = PRODUCT_ANALYSIS_PROMPT.format(caption=caption)
                    llm_structured = llm.with_structured_output(ProductModels)

                    logging.info("Invoking LLM for structured product extraction")
                    response: ProductModels = await llm_structured.ainvoke([
                        HumanMessage(content=prompt)
                    ])
                    logging.info(f"LLM structured output received: {len(response.product_description)} product(s) extracted")
                    return response

                case _:
                    logging.error(f"Unsupported content_type: {content_type} for path: {content_path}")
                    raise MyException(f"content_type '{content_type}' is not supported right now", sys)

        except MyException:
            raise
        except Exception as e:
            logging.error(f"ResourceAnalyserComponent.analyse — error: {e}")
            raise MyException(e, sys)
