from fastapi import APIRouter

from app.api.routes import auth, problems, submissions, teacher

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(problems.router)
api_router.include_router(submissions.router)
api_router.include_router(teacher.router)
