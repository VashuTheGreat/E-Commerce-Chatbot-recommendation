from api.main import app
from src.logger import *
import uvicorn


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=7860,reload=True)