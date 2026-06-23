from fastapi import FastAPI

from api.routes.training_route import router as TrainingRoute
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI(title="E-Commerce Chatbot API")
# templates = Jinja2Templates(directory="api/templates")

# app.include_router(llm_router, prefix="/api/llm", tags=["LLM"])
# app.include_router(ECRrouter, prefix="/api/retreive", tags=["Retreive"])
# app.include_router(TRAINrouter, prefix="/api/train", tags=["Train"])

app.include_router(prefix="/api/v1/model",router=TrainingRoute)
