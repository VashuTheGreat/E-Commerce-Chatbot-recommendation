from fastapi import APIRouter
from src.ECRecom.pipelines.prediction_pipeline import PredictionPipeline

router = APIRouter()

@router.post("/")
async def retreive_docs(query: str, k: int = 5):
    try:
        pipeline = PredictionPipeline()
        docs = await pipeline.initiate(query=query, k=k)
        
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
