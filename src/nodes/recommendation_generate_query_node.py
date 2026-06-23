import logging
from langchain_core.messages import SystemMessage, HumanMessage
from src.models.orchastrator_state import State
from src.llm.llm_loader import llm
from src.utils.asyncHandler import asyncHandler
from src.prompts import QUERY_GENERATOR_PROMPT

logger = logging.getLogger(__name__)

@asyncHandler
async def generate_query_node(state: State):
    messages = state.get("messages", [])
    image_paths = state.get("analyse_content_paths", [])

    has_image = bool(image_paths) and "000" not in image_paths

    last_user_query = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            last_user_query = msg.content
            break

    if not last_user_query.strip():
        return {
            "search_query": "",
            "messages": messages
        }

    prompt = QUERY_GENERATOR_PROMPT.format(
        last_user_query=last_user_query,
        image_provided='yes' if has_image else 'no'
    )

    response = await llm.ainvoke([SystemMessage(content=prompt)])
    search_query = response.content.strip()
    search_query = " ".join(search_query.split())

    return {
        "search_query": search_query,
        "messages": messages
    }
