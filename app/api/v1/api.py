from fastapi import APIRouter

from app.api.v1.endpoints import login, users, cycles, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(cycles.router, prefix="/cycles", tags=["cycles"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
