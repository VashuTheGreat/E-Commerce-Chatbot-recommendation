import logging
from langgraph.checkpoint.memory import MemorySaver

logging.info("Initialising InMemorySaver checkpointer")
memory = MemorySaver()
logging.info("InMemorySaver checkpointer ready")