from fastapi import FastAPI
from api.routes.training_route import router as TrainingRoute
from api.routes.agents_route import router as AgentRoute
from api.routes.user_routes import router as UserRoute


app = FastAPI(title="E-Commerce Chatbot API")

app.include_router(prefix="/api/v1/model", router=TrainingRoute)
app.include_router(prefix="/api/v1/agent", router=AgentRoute)
app.include_router(prefix="/api/v1/user", router=UserRoute)
