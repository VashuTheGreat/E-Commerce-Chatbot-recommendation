from langchain_groq import ChatGroq
from src.LLMResponse.constants import CHAT_MODEL_NAME
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model=CHAT_MODEL_NAME,
    api_key=os.getenv("GROQ_API_KEY")
)