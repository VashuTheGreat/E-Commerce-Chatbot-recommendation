from utils.asyncHandler import asyncHandler
from src.LLMResponse.entity import State, ImageComponents
from src.LLMResponse.llm.llm_loader import llm
from src.LLMResponse.prompts import CHAT_LLM_PROMPT
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

@asyncHandler
async def chat_llm_node(state: State):
    parser = PydanticOutputParser(pydantic_object=ImageComponents)
    prompt = ChatPromptTemplate.from_template(CHAT_LLM_PROMPT + "\n{format_instructions}")
    prompt = prompt.partial(format_instructions=parser.get_format_instructions())
    chain = prompt | llm | parser
    try:
        res = await chain.ainvoke({
            "user_query": state.user_query or "",
            "image_summary": state.image_summary or ""
        })
        fields = []
        for p in res.image_discription:
            for v in p.model_dump().values():
                if v: fields.append(str(v).lower())
        state.llm_query = " ".join(fields)
    except:
        state.llm_query = str(state.image_summary).lower()
    return state