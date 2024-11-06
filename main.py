# File: main.py

from fastapi import FastAPI
from endpoints import router
import uvicorn
from file_service import FileManager

app = FastAPI(title="Regional Language Translation API")
file_manager = FileManager()

# Include all routes from endpoints.py
app.include_router(router, prefix="")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)