import logging
from langchain_core.messages import SystemMessage
from src.LLMResponse.models.orchastrator_state import State
from src.LLMResponse.llm.llm_loader import llm
from src.LLMResponse.tools.data_fetcher_tool import fetch_recommendations_from_db
from src.LLMResponse.prompts import ORCHESTRATOR_SYSTEM_PROMPT


llm_with_tools = llm.bind_tools([fetch_recommendations_from_db])

from utils.asyncHandler import asyncHandler

@asyncHandler
async def orchestrator(state: State) -> dict:
    logging.info("orchestrator — entered node")
    logging.debug(f"orchestrator — current message count: {len(state['messages'])}")

    system_msg = SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT)
    messages = [system_msg] + state["messages"]

    logging.info("orchestrator — invoking LLM with tools bound")
    response = await llm_with_tools.ainvoke(messages)

    if response.tool_calls:
        logging.info(f"orchestrator — LLM requested tool calls: {[tc['name'] for tc in response.tool_calls]}")
    else:
        logging.info("orchestrator — LLM produced a direct response (no tool calls)")

    return {"messages": [response]}
