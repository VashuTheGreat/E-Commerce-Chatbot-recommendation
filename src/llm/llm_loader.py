import logging
from langchain_groq import ChatGroq
from src.constants import CHAT_MODEL_NAME
from src.config.app_config import app_config

logging.info("loading LLM model configuration")
llm = ChatGroq(
    model=CHAT_MODEL_NAME,
    api_key=app_config.groq_api_key
)
logging.info(f"LLM model initialized: {CHAT_MODEL_NAME}")