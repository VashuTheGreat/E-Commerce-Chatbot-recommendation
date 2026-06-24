from fastapi import Request, HTTPException

async def authenticate_user(request: Request):
    thread_id = request.cookies.get("thread_id")
    if not thread_id:
        raise HTTPException(
            status_code=401,
            detail={"success": False, "message": "Please login", "data": None}
        )

    request.state["user_id"] = thread_id