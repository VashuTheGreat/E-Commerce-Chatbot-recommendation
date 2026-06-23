import logging
from typing import Literal
from langchain_core.messages import HumanMessage
from src.models.orchastrator_state import State
from src.utils.asyncHandler import asyncHandler

logger = logging.getLogger(__name__)

_SIMPLE_PATTERNS = {
    "hello", "hi", "hey", "hola", "yo",
    "good morning", "good afternoon", "good evening", "good night",
    "thanks", "thank you", "thx", "ty", "appreciate it",
    "bye", "goodbye", "see you", "later", "cya",
    "ok", "okay", "k", "cool", "nice", "great", "awesome", "perfect", "got it",
    "ok thanks", "ok thank you", "thanks bye", "thank you bye", "ok bye",
}

def _is_simple_query(text: str) -> bool:
    text_lower = text.lower().strip().rstrip("!?.")
    if text_lower in _SIMPLE_PATTERNS:
        return True
    if len(text_lower) < 20 and not any(
        keyword in text_lower
        for keyword in ["men", "women", "watch", "product", "shoes", "shirt", "dress", "jeans", "bag", "accessories", "buy", "search", "find", "look for", "recommend"]
    ):
        return True
    return False

@asyncHandler
async def router_node(state: State):
    image_paths = state.get("analyse_content_paths", [])
    has_image = bool(image_paths) and "000" not in image_paths
    if has_image:
        return {"query_type": "complex"}
    messages = state.get("messages", [])
    if not messages:
        return {"query_type": "simple"}
    last_msg = messages[-1]
    if not isinstance(last_msg, HumanMessage):
        return {"query_type": "simple"}
    user_text = last_msg.content.strip()
    if _is_simple_query(user_text):
        return {"query_type": "simple"}
    return {"query_type": "complex"}

def router_router(state: State) -> Literal["simple_chat", "generate_query"]:
    return state.get("query_type", "complex")
