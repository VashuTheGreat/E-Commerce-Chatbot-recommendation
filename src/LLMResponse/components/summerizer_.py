from src.LLMResponse.llm.llm_loader import llm

async def invoke(query: str, response: list):
    prompt = f"You are given with user query and the response retrieved by the ai powered database. Summarize the response and suggest user what to take. Output must be in markdown. Never Mension any url just write beutiful markdown code with your suggestion\nUser Query: {query}\nDatabase Response: {response}"
    res = await llm.ainvoke(prompt)
    return res.content
