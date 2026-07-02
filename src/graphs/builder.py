import logging
from langgraph.graph import START, END, StateGraph
from src.models.agent_models import State
from src.nodes.agents_nodes import (
    orchestrator,
    chat,
    retreiver_node,
    retriever_node_v2,
    tools,
    analyse_image_node
)
from langgraph.prebuilt import ToolNode, tools_condition
from src.memmory import memory
from src.utils.asyncHandler import asyncHandler

logging.info("Initializing graph builder")

workflow = StateGraph(State)

logging.info("Adding orchestrator node")
workflow.add_node("orchestrator", orchestrator)
logging.info("Adding chat node")
workflow.add_node("chat", chat)

workflow.add_node("analyse_image_node", analyse_image_node)

# ── [DEPRECATED] old single-index retriever ─────────────────────────────────
logging.info("Adding retreiver node (deprecated, kept for backward compatibility)")
workflow.add_node("retreiver", retreiver_node)

# ── New dual-index retriever (image index + text index, fused with RRF) ──────
logging.info("Adding retriever_v2 node")
workflow.add_node("retriever_v2", retriever_node_v2)

logging.info("Adding tools node")
workflow.add_node("tools", ToolNode(tools))

# ── START: if image uploaded → analyse first, else → orchestrator directly ────
def route_start(state):
    if state.get("image_path") and state.get("img_caption") is None:
        logging.info("route_start: image present and not yet captioned → analyse_image_node")
        return "analyse_image_node"
    logging.info("route_start: no image (or already captioned) → orchestrator")
    return "orchestrator"

logging.info("Adding conditional edge from START")
workflow.add_conditional_edges(
    START,
    route_start,
    {
        "analyse_image_node": "analyse_image_node",
        "orchestrator": "orchestrator",
    }
)

# analyse_image_node always feeds into orchestrator (caption is ready by then)
workflow.add_edge("analyse_image_node", "orchestrator")

def route_orchestrator(state):
    target = state.get("redirect_to", "chat_node")
    logging.info(f"route_orchestrator conditional edge evaluated target: {target}")
    return target

logging.info("Adding conditional edges from orchestrator")
workflow.add_conditional_edges(
    "orchestrator",
    route_orchestrator,
    {
        "chat_node": "chat",
        # Route to the new dual-index retriever
        # (old 'retreiver' node kept registered but no longer the default target)
        "retreiver_node": "retriever_v2",
    }
)

# Both retriever nodes feed into chat
logging.info("Adding edge from retreiver (deprecated) to chat")
workflow.add_edge("retreiver", "chat")
logging.info("Adding edge from retriever_v2 to chat")
workflow.add_edge("retriever_v2", "chat")

logging.info("Adding conditional edges from chat to tools or END")
workflow.add_conditional_edges(
    "chat",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)
logging.info("Adding edge from tools to chat")
workflow.add_edge("tools", "chat")

logging.info("Compiling graph workflow with memory checkpointer")
graph = workflow.compile(checkpointer=memory)
logging.info("Graph workflow compiled successfully")

try:
    with open("graph.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    logging.info("Graph PNG diagram saved")
except Exception as e:
    logging.error(f"Failed to save graph diagram: {e}")




@asyncHandler
async def deleteThread(thread_id: str):
    logging.info(f"deleteThread called for thread_id: {thread_id}")
    try:
        cp = memory
        state = await cp.aget_tuple(config={'configurable': {'thread_id': thread_id}})
        if state is None:
            logging.info(f"Thread {thread_id} not found, nothing to delete.")
            return False
        await cp.adelete_thread(thread_id=thread_id)
        logging.info(f"Thread {thread_id} deleted successfully.")
        return True
    except Exception as e:
        logging.error(f"Error deleting thread {thread_id}: {e}")
        return False

@asyncHandler
async def load_conversation(thread_id):
    logging.info(f"load_conversation called for thread_id: {thread_id}")
    try:
        state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
        messages = state.values.get('messages', [])
        logging.info(f"load_conversation succeeded. retrieved {len(messages)} messages.")
        return messages
    except Exception as e:
        logging.error(f"Error loading conversation: {e}")
        return []