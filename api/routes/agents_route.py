import logging
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from src.pipelines.graph_runner_pipeline import GraphRunnerPipeline
from api.models.chat_agent_models import ChatAgentModel
from api.middlewares.multer_middleware import multer_middleware
from api.middlewares.authenticate_user_middleware import authenticate_user


logging.info("POST /chat - instantiating graph runner pipeline")
graph_runner_pipeline = GraphRunnerPipeline()
logging.info("POST /chat - calling initiate on pipeline")

router = APIRouter()

@router.post("/chat",dependencies=[Depends(authenticate_user)])
async def chat(body: ChatAgentModel, file: str = Depends(multer_middleware)):
    logging.info(f"POST /chat endpoint called with thread_id: {body.thread_id}, message: '{body.message}'")
    logging.info(f"POST /chat file upload path from middleware: '{file}'")
    try:
        res = StreamingResponse(graph_runner_pipeline.initiate(
            thread_id=body.thread_id,
            query=body.message,
            image_path=file
        ),media_type="text/event-stream")
        if not res:
            logging.error("POST /chat - agent execution returned empty or invalid response")
            raise HTTPException(
                status_code=500,
                detail={"data": None, "message": "Agent execution failed", "success": False}
            )
        logging.info("POST /chat - agent execution succeeded, returning StreamingResponse")
        return res
    except Exception as e:
        logging.error(f"POST /chat - exception during request execution: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={"data": None, "message": str(e), "success": False}
        )
