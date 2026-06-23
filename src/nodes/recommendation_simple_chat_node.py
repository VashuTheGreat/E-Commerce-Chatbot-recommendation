from langchain_core.messages import AIMessage, HumanMessage
from src.models.orchastrator_state import State
from src.utils.asyncHandler import asyncHandler

@asyncHandler
async def simple_chat_node(state: State):
    messages = state.get("messages", [])
    user_text = messages[-1].content.lower().strip() if messages and isinstance(messages[-1], HumanMessage) else ""

    if any(word in user_text for word in ["hello", "hi", "hey", "hola"]) or user_text in {"hello", "hi", "hey", "hola", "yo"}:
        response = "Hello! How can I help you today?"
    elif any(word in user_text for word in ["thank", "thx", "ty", "appreciate"]):
        response = "You're welcome! Let me know if you need anything else."
    elif any(word in user_text for word in ["bye", "goodbye", "see you", "cya"]) or user_text in {"bye", "goodbye", "see you", "cya"}:
        response = "Goodbye! Have a great day!"
    elif "how are you" in user_text:
        response = "I'm doing well, thanks for asking! How can I help you today?"
    else:
        response = "I understand. Let me know if you need help finding anything!"

    return {
        "final_response": response,
        "messages": [AIMessage(content=response)],
        "db_results": []
    }
