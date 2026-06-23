from langchain_core.messages import SystemMessage
from src.models.orchastrator_state import State
from src.llm.llm_loader import llm
from src.utils.asyncHandler import asyncHandler
from src.prompts import FINAL_CHAT_SYSTEM_PROMPT

@asyncHandler
async def final_chat_node(state: State):
    messages = state.get("messages", [])
    db_results = state.get("db_results", [])
    search_query = state.get("search_query", "")

    if db_results:
        products_text = "\n".join(
            f"- Product ID: {match.get('metadata', {}).get('row_id', 'N/A')}, Score: {match.get('score', 'N/A'):.4f}"
            for match in db_results[:5]
        )
        context = f"Search results for '{search_query}':\n\n{products_text}"
    else:
        context = f"No products were found for the query '{search_query}'."

    system_msg = SystemMessage(
        content=FINAL_CHAT_SYSTEM_PROMPT.format(context=context)
    )

    llm_messages = [system_msg] + messages
    response = await llm.ainvoke(llm_messages)

    return {
        "final_response": response.content,
        "messages": [response],
        "db_results": db_results
    }
