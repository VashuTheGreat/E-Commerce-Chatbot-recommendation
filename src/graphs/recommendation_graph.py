import logging
from langgraph.graph import StateGraph, START, END
from src.models.orchastrator_state import State
from src.nodes.recommendation_router_node import router_node, router_router
from src.nodes.recommendation_simple_chat_node import simple_chat_node
from src.nodes.recommendation_generate_query_node import generate_query_node
from src.nodes.recommendation_retriever_node import retriever_node
from src.nodes.recommendation_final_chat_node import final_chat_node

logger = logging.getLogger(__name__)

def create_graph():
    workflow = StateGraph(State)
    workflow.add_node("router", router_node)
    workflow.add_node("simple_chat", simple_chat_node)
    workflow.add_node("generate_query", generate_query_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("final_chat", final_chat_node)

    workflow.add_edge(START, "router")
    workflow.add_conditional_edges(
        "router",
        router_router,
        {
            "simple_chat": "simple_chat",
            "generate_query": "generate_query",
        },
    )
    workflow.add_edge("simple_chat", END)
    workflow.add_edge("generate_query", "retriever")
    workflow.add_edge("retriever", "final_chat")
    workflow.add_edge("final_chat", END)

    return workflow.compile()

graph = create_graph()
