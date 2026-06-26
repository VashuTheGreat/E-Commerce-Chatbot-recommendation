from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from api.routes.training_route import router as TrainingRoute
from api.routes.agents_route import router as AgentRoute
from api.routes.user_routes import router as UserRoute
from api.routes.common_routes import router as CommonRoute
from api.routes.page_routes import router as PageRoute

API_DIR = Path(__file__).resolve().parent

app = FastAPI(title="E-Commerce Chatbot API")

app.mount("/static", StaticFiles(directory=API_DIR / "static"), name="static")

app.include_router(prefix="/api/v1/model", router=TrainingRoute)
app.include_router(prefix="/api/v1/agent", router=AgentRoute)
app.include_router(prefix="/api/v1/user", router=UserRoute)
app.include_router(prefix="/api/v1/common", router=CommonRoute)
app.include_router(router=PageRoute)
