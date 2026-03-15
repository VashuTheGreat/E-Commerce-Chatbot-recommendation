from api.main import app 
import uvicorn
import os

os.makedirs("tempImage",exist_ok=True)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)