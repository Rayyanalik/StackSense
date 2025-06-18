from fastapi import APIRouter
from app.api.v1.endpoints import tech_stack

api_router = APIRouter()
api_router.include_router(tech_stack.router, tags=["tech-stack"]) 