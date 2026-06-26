from fastapi import APIRouter
from fastapi.responses import JSONResponse

router =APIRouter()


@router.get("/health")
async def health():
    return JSONResponse(status_code=200,content={"data":None,"message":"Server is fit and fine","success":True})


@router.get("/available_time")
async def available_time():
    TIME_OPTIONS = [
    {
        "label": "1 Minute",
        "description": "Quick demo or sanity check",
        "icon": "⚡",
        "seconds": 60,
    },
    {
        "label": "2 Minutes",
        "description": "Standard exploration session",
        "icon": "🧪",
        "seconds": 120,
    },
    {
        "label": "3 Minutes",
        "description": "Deep-dive knowledge session",
        "icon": "🔬",
        "seconds": 180,
    },
     {
        "label": "10 Minutes",
        "description": "Very Deep-dive knowledge session",
        "icon": "🔬",
        "seconds": 300,
    }
    ]
    return JSONResponse(status_code=200,content={"data":TIME_OPTIONS,"message":"Server is fit and fine","success":True})

