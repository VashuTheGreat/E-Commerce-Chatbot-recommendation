from fastapi import APIRouter
from pydantic import BaseModel
from src.ECRecom.pipelines.prediction_pipeline import PredictionPipeline

router = APIRouter()

class RetrieveRequest(BaseModel):
    query: str
    k: int = 5

@router.post("/")
async def retreive_docs(request: RetrieveRequest):
    try:
        pipeline = PredictionPipeline()
        docs = await pipeline.initiate(query=request.query, k=request.k)
        
        results = []
        for doc in docs:
            results.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata
            })
            
        return {
            "status": "success",
            "results": results
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
