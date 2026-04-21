import logging
import json
from langchain_core.messages import SystemMessage, AIMessage, ToolMessage, HumanMessage
from src.LLMResponse.models.orchastrator_state import State
from src.LLMResponse.llm.llm_loader import llm
from src.LLMResponse.prompts import CHAT_LLM_SYSTEM_PROMPT
from utils.asyncHandler import asyncHandler


def _get_current_turn_tool_msg(messages: list) -> ToolMessage | None:
    last_human_idx = next(
        (i for i in range(len(messages) - 1, -1, -1) if isinstance(messages[i], HumanMessage)),
        None
    )
    if last_human_idx is None:
        return None
    return next(
        (m for m in messages[last_human_idx:]
         if isinstance(m, ToolMessage) and m.name == "fetch_recommendations_from_db"),
        None
    )


def _trim_tool_message(msg: ToolMessage) -> ToolMessage:
    try:
        parsed = json.loads(msg.content)
        if isinstance(parsed, dict) and "results" in parsed:
            clean_results = [{"page_content": r.get("page_content", "")} for r in parsed["results"]]
            return ToolMessage(
                content=json.dumps({"status": "success", "results": clean_results}),
                name=msg.name,
                tool_call_id=msg.tool_call_id
            )
    except Exception:
        pass
    return msg


def _build_filtered_messages(messages: list) -> list:
    filtered = [
        _trim_tool_message(msg)
        if (isinstance(msg, ToolMessage) and msg.name == "fetch_recommendations_from_db")
        else msg
        for msg in messages
    ]
    if filtered and isinstance(filtered[-1], AIMessage) and not filtered[-1].tool_calls:
        filtered.pop()
    return filtered


@asyncHandler
async def chat_llm_node(state: State) -> dict:
    logging.info("chat_llm_node — entered node")
    logging.debug(f"chat_llm_node — total messages in history: {len(state['messages'])}")

    messages = state["messages"]

    current_tool_msg = _get_current_turn_tool_msg(messages)
    db_results = []
    if current_tool_msg is not None:
        try:
            parsed = json.loads(current_tool_msg.content)
            if isinstance(parsed, dict) and "results" in parsed:
                db_results = parsed["results"]
                logging.info(f"chat_llm_node — extracted {len(db_results)} db_results from current turn")
        except Exception:
            pass

    filtered_messages = _build_filtered_messages(messages)
    messages_for_llm = [SystemMessage(content=CHAT_LLM_SYSTEM_PROMPT)] + filtered_messages

    logging.info("chat_llm_node — invoking LLM")
    response: AIMessage = await llm.ainvoke(messages_for_llm)

    logging.info("chat_llm_node — response generated")
    logging.debug(f"chat_llm_node — response preview: {response.content[:200]}...")

    return {
        "messages": [response],
        "final_response": response.content,
        "db_results": db_results,
    }