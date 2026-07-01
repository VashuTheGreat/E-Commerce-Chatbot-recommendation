from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

API_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(API_DIR / "templates"))

router = APIRouter()


@router.get("/")
async def home_page(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})



@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@router.get("/train")
async def train_page(request: Request):
    return templates.TemplateResponse("train.html", {"request": request})


@router.get("/health")
async def health_page(request: Request):
    return templates.TemplateResponse("health.html", {"request": request})
