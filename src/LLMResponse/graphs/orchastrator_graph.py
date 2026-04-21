import logging
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AIMessage

from src.LLMResponse.models.orchastrator_state import State
from src.LLMResponse.nodes.chat_llm_node import chat_llm_node
from src.LLMResponse.nodes.orchastrator_node import orchestrator
from src.LLMResponse.nodes.resource_analyser_node import resource_analyser
from src.LLMResponse.tools.data_fetcher_tool import fetch_recommendations_from_db
from src.LLMResponse.memmory import memory


def _orchestrator_router(state: State) -> str:
    
    paths = state.get("analyse_content_paths", [])
    analysis = state.get("uploaded_content_analysis", [])

    if paths and not analysis:
        logging.info("orchestrator_router — images present but not analysed yet → routing to resource_analyser")
        return "resource_analyser"

    messages = state["messages"]
    last_msg = messages[-1] if messages else None

    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
        logging.info(f"orchestrator_router — LLM requested tools {[tc['name'] for tc in last_msg.tool_calls]} → routing to tool_node")
        return "tool_node"

    logging.info("orchestrator_router — no pending work → routing to chat_llm")
    return "chat_llm"


def create_graph():
    logging.info("create_graph — building LangGraph workflow")

    workflow = StateGraph(State)

    workflow.add_node("orchestrator", orchestrator)
    workflow.add_node("resource_analyser", resource_analyser)
    workflow.add_node("tool_node", ToolNode([fetch_recommendations_from_db]))
    workflow.add_node("chat_llm", chat_llm_node)

    workflow.add_edge(START, "orchestrator")

    workflow.add_conditional_edges(
        "orchestrator",
        _orchestrator_router,
        {
            "resource_analyser": "resource_analyser",
            "tool_node": "tool_node",
            "chat_llm": "chat_llm",
        }
    )

    workflow.add_edge("resource_analyser", "orchestrator")

    workflow.add_edge("tool_node", "orchestrator")

    workflow.add_edge("chat_llm", END)

    graph = workflow.compile(checkpointer=memory)
    logging.info("create_graph — graph compiled successfully with InMemorySaver checkpointer")
    return graph


graph = create_graph()

try:
    with open("workflow.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    logging.info("Graph diagram saved to workflow.png")
except Exception as e:
    logging.warning(f"Could not save workflow diagram: {e}")
