
from fastapi import APIRouter
from app.api.v1.endpoints import auth, documents
from app.api.v1.endpoints import study_rooms

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticacion"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(study_rooms.router, prefix="/study-rooms", tags=["Study Rooms"])