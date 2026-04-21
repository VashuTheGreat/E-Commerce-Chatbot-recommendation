import logging
import json
from langchain_core.messages import ToolMessage
from src.LLMResponse.models.orchastrator_state import State
from src.LLMResponse.components.uploaded_resourse_analyser import ResourceAnalyserComponent

from utils.asyncHandler import asyncHandler

@asyncHandler
async def resource_analyser(state: State) -> dict:
    logging.info("resource_analyser — entered node")

    paths = state.get("analyse_content_paths", [])
    logging.info(f"resource_analyser — {len(paths)} file(s) to analyse: {paths}")

    if not paths:
        logging.warning("resource_analyser — no content paths found in state, returning empty ToolMessage")
        tool_msg = ToolMessage(
            content="No images were provided for analysis.",
            tool_call_id="resource_analyser"
        )
        return {"messages": [tool_msg]}

    analyser = ResourceAnalyserComponent()
    all_results: list[dict] = []

    for path in paths:
        logging.info(f"resource_analyser — analysing: {path}")
        try:
            result = await analyser.analyse(path)
            products = [p.model_dump(exclude_none=True) for p in result.product_description]
            all_results.extend(products)
            logging.info(f"resource_analyser — extracted {len(products)} product(s) from {path}")
        except Exception as e:
            logging.error(f"resource_analyser — failed to analyse {path}: {e}")

    summary = json.dumps(all_results, indent=2)
    logging.info(f"resource_analyser — total products extracted across all images: {len(all_results)}")
    logging.debug(f"resource_analyser — full analysis result:\n{summary}")

    tool_msg = ToolMessage(
        content=f"Image analysis complete. Extracted product details:\n{summary}",
        tool_call_id="resource_analyser"
    )

    return {
        "messages": [tool_msg],
        "uploaded_content_analysis": all_results
    }
