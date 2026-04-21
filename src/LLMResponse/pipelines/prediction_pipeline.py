import logging
from typing import List, Optional
from langchain_core.messages import HumanMessage
from src.LLMResponse.graphs.orchastrator_graph import graph
from utils.asyncHandler import asyncHandler

@asyncHandler
async def run_llm_response_pipeline(
    user_query: str,
    thread_id: str,
    image_paths: Optional[List[str]] = None
) -> dict:
    logging.info(f"run_llm_response_pipeline — started | thread_id={thread_id} | query='{user_query}' | images={image_paths}")

    from src.LLMResponse.tools.data_fetcher_tool import fetcher_instance
    fetcher_instance.reset()

    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "analyse_content_paths": image_paths or [],
        "uploaded_content_analysis": [],
        "db_results": [],
        "final_response": None,
    }

    config = {"configurable": {"thread_id": thread_id}}

    logging.info("run_llm_response_pipeline — invoking graph")
    result = await graph.ainvoke(initial_state, config=config)

    final_response = result.get("final_response", "")
    db_results = result.get("db_results", [])

    logging.info(f"run_llm_response_pipeline — completed | db_results count={len(db_results)}")
    logging.debug(f"run_llm_response_pipeline — final_response preview: {str(final_response)[:200]}")

    return {
        "final_response": final_response,
        "db_results": db_results,
        "messages": [m.dict() if hasattr(m, "dict") else str(m) for m in result.get("messages", [])],
    }
