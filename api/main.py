from fastapi import FastAPI
from api.LLMResponse.routes.llm_query_routes import router as llm_router
from api.ECRecom.routes.retreiver_rel_docs import router as ECRrouter
from api.ECRecom.routes.trainer_routes import router as TRAINrouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import Request

app = FastAPI(title="E-Commerce Chatbot API")
templates = Jinja2Templates(directory="api/templates")

app.include_router(llm_router, prefix="/api/llm", tags=["LLM"])
app.include_router(ECRrouter, prefix="/api/retreive", tags=["Retreive"])
app.include_router(TRAINrouter, prefix="/api/train", tags=["Train"])
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})
