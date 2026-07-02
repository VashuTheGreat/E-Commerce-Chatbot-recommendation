# Exact-match / direct search graph
# Used by the search API (Amazon-style text search + image similarity tab)
# Flow: START -> retriever_v2 -> END

import logging
from langgraph.graph import START, END, StateGraph
from src.models.agent_models import Exact_Matcher_State
from src.nodes.agents_nodes import retriever_node_v2

logging.info("[builder2] Initializing Exact-Matcher workflow")

workflow = StateGraph(Exact_Matcher_State)

logging.info("[builder2] Adding retriever_v2 node")
workflow.add_node("retriever_v2", retriever_node_v2)

logging.info("[builder2] Adding START -> retriever_v2 edge")
workflow.add_edge(START, "retriever_v2")

logging.info("[builder2] Adding retriever_v2 -> END edge")
workflow.add_edge("retriever_v2", END)

logging.info("[builder2] Compiling graph")
exact_match_graph = workflow.compile()
logging.info("[builder2] Graph compiled successfully")

try:
    with open("exact_match_workflow.png", "wb") as f:
        f.write(exact_match_graph.get_graph().draw_mermaid_png())
    logging.info("[builder2] Graph PNG diagram saved")
except Exception as e:
    logging.error(f"[builder2] Failed to save graph diagram: {e}")
