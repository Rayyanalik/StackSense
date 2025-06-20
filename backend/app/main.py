from fastapi import FastAPI, Request
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.logging import logger
import os
import time
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="StackSense API",
    description="API for tech stack recommendations",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add error handler middleware
@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}")
        return {"error": "Internal server error"}, 500

# Add favicon handler
@app.get("/favicon.ico")
async def favicon():
    return FileResponse("static/favicon.ico")

# Include API router with the correct prefix
app.include_router(api_router, prefix="/api/v1/tech-stack")

@app.get("/")
def read_root():
    return {"message": "StackSense API is running!"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": time.time()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 