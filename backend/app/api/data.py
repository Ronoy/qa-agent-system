from fastapi import APIRouter
from app.mock.data import get_attendance_data, get_learning_data, get_task_data, get_knowledge_data

router = APIRouter()

@router.get("/attendance")
async def attendance():
    return get_attendance_data()

@router.get("/learning")
async def learning():
    return get_learning_data()

@router.get("/tasks")
async def tasks():
    return get_task_data()

@router.get("/knowledge")
async def knowledge():
    return get_knowledge_data()
