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
    
    return templates.TemplateResponse(request=request,
    name="home.html",
    context={})



@router.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse(request=request,
    name="login.html",
    context={})


@router.get("/chat")
async def chat_page(request: Request):
    return templates.TemplateResponse(request=request,
    name="chat.html",
    context={})


@router.get("/train")
async def train_page(request: Request):
    return templates.TemplateResponse(request=request,
    name="train.html",
    context={})


@router.get("/health")
async def health_page(request: Request):
    return templates.TemplateResponse(request=request,
    name="health.html",
    context={})
