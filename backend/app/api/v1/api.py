from fastapi import APIRouter

from app.api.v1 import editorial

api_router = APIRouter()

api_router.include_router(editorial.router, prefix="/editorial", tags=["Editorial"])
