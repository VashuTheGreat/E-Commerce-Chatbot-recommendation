from langgraph.graph import StateGraph, START, END
from src.LLMResponse.entity import State
from src.LLMResponse.nodes.image_summerizer_node import image_summerizer_node
from src.LLMResponse.nodes.chat_llm_node import chat_llm_node

def create_graph():
    workflow = StateGraph(State)
    workflow.add_node("image_summarizer", image_summerizer_node)
    workflow.add_node("chat_llm", chat_llm_node)
    workflow.add_edge(START, "image_summarizer")
    workflow.add_edge("image_summarizer", "chat_llm")
    workflow.add_edge("chat_llm", END)
    return workflow.compile()

graph = create_graph()
