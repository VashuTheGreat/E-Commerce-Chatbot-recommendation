import logging
import json
from langchain_core.messages import SystemMessage, AIMessage
from src.LLMResponse.models.orchastrator_state import State
from src.LLMResponse.llm.llm_loader import llm
from src.LLMResponse.prompts import CHAT_LLM_SYSTEM_PROMPT
from utils.asyncHandler import asyncHandler

@asyncHandler
async def chat_llm_node(state: State) -> dict:
    logging.info("chat_llm_node — entered node")
    logging.debug(f"chat_llm_node — total messages in history: {len(state['messages'])}")

    db_results = state.get("db_results", [])
    if not db_results:
        for msg in state["messages"]:
            if hasattr(msg, "name") and msg.name == "fetch_recommendations_from_db":
                try:
                    parsed = json.loads(msg.content)
                    if isinstance(parsed, dict) and "results" in parsed:
                        db_results = parsed["results"]
                        logging.info(f"chat_llm_node — extracted {len(db_results)} db_results from ToolMessage history")
                except Exception:
                    pass

    filtered_messages = []
    from langchain_core.messages import ToolMessage
    for msg in state["messages"]:
        if hasattr(msg, "name") and msg.name == "fetch_recommendations_from_db":
            try:
                parsed = json.loads(msg.content)
                if isinstance(parsed, dict) and "results" in parsed:
                    clean_results = [{"page_content": r.get("page_content", "")} for r in parsed["results"]]
                    clean_content = json.dumps({"status": "success", "results": clean_results})
                    
                    clean_msg = ToolMessage(content=clean_content, name=msg.name, tool_call_id=msg.tool_call_id)
                    filtered_messages.append(clean_msg)
                    continue
            except Exception:
                pass
        filtered_messages.append(msg)

    if filtered_messages and isinstance(filtered_messages[-1], AIMessage) and not filtered_messages[-1].tool_calls:
        filtered_messages.pop()
                
    system_msg = SystemMessage(content=CHAT_LLM_SYSTEM_PROMPT)
    messages_for_llm = [system_msg] + filtered_messages

    logging.info("chat_llm_node — invoking LLM for final response generation")
    response: AIMessage = await llm.ainvoke(messages_for_llm)

    final_text = response.content
    logging.info("chat_llm_node — final response generated successfully")
    logging.debug(f"chat_llm_node — response preview: {final_text[:200]}...")

    return {
        "messages": [response],
        "final_response": final_text,
        "db_results": db_results
    }