from utils.asyncHandler import asyncHandler
from src.LLMResponse.entity import State
from src.LLMResponse.llm.llm_loader import llm
from langchain_core.output_parsers import StrOutputParser

@asyncHandler
async def summary_node(state: State):
    prompt = "you are a selling assistant you are given with a json type of data summarize the content in natural language and ask the user that do you need any other thing i can help you with"
    parser = StrOutputParser()
    chain = llm | parser
    r = await chain.ainvoke(f"{prompt} state data: {str(state.model_dump())}")
    state.summary = r
    return state
