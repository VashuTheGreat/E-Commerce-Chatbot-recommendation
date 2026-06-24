import logging
from langgraph.graph import START, END, StateGraph
from src.models.agent_models import State
from src.nodes.agents_nodes import orchestrator, chat, retreiver_node, tools
from langgraph.prebuilt import ToolNode, tools_condition
from src.memmory import memory
from src.utils.asyncHandler import asyncHandler
logging.info("Initializing graph builder")

workflow = StateGraph(State)

workflow.add_node("orchestrator", orchestrator)
workflow.add_node("chat", chat)
workflow.add_node("retreiver", retreiver_node)
workflow.add_node("tools", ToolNode(tools))

workflow.add_edge(START, "orchestrator")

workflow.add_conditional_edges(
    "orchestrator",
    lambda state: state.get("redirect_to", "chat_node"),
    {
        "chat_node": "chat",
        "retreiver_node": "retreiver"
    }
)

workflow.add_edge("retreiver", "chat")

workflow.add_conditional_edges(
    "chat",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)
workflow.add_edge("tools", "chat")

graph = workflow.compile(checkpointer=memory)

try:
    with open("graph.png", "wb") as f:
        f.write(graph.get_graph().draw_mermaid_png())
    logging.info("Graph PNG diagram saved")
except Exception as e:
    logging.error(f"Failed to save graph diagram: {e}")




@asyncHandler
async def deleteThread(thread_id: str):
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
    try:
        state = graph.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('messages', [])
    except Exception as e:
        logging.error(f"Error loading conversation: {e}")
        return []