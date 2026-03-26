from fastapi import APIRouter
from app.api.v1 import pautas, generation, wordpress

api_router = APIRouter()

# Incluir as rotas com seus respectivos prefixos e tags
api_router.include_router(pautas.router, prefix="/pautas", tags=["Pautas"])
api_router.include_router(generation.router, prefix="/generation", tags=["Geração"])
api_router.include_router(wordpress.router, prefix="/wordpress", tags=["WordPress"])
