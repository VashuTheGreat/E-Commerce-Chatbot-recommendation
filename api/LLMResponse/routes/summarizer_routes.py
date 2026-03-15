from fastapi import APIRouter, Body
from src.LLMResponse.components.summerizer_ import invoke

router = APIRouter()

@router.post("/")
async def summarize_response(query: str, response: list = Body(...)):
    try:
        md_summary = await invoke(query, response)
        return {"status": "success", "summary": md_summary}
    except Exception as e:
        return {"status": "error", "message": str(e)}
