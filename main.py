# File: main.py

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from endpoints import router
import uvicorn
from file_service import FileManager
import os

app = FastAPI(title="Regional Language Translation API")
file_manager = FileManager()

# Include all routes from endpoints.py
app.include_router(router, prefix="/api")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_docs():
    """Serve the documentation HTML file"""
    return FileResponse('docs.html')

@app.get("/readme")
async def read_readme():
    """Serve the README.md file directly"""
    return FileResponse('readme.md')

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)