<<<<<<< HEAD
from fastapi import APIRouter, Depends
from motor.core import AgnosticDatabase
from app.database import get_database

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/")
async def get_news(db: AgnosticDatabase = Depends(get_database)):
    # Здесь можно получать новости из БД или возвращать статические данные
    return [
        {"title": "Новые поступления iPhone 15", "date": "2025-07-20"},
        {"title": "Акция на ремонт техники", "date": "2025-07-15"}
=======
from fastapi import APIRouter, Depends
from motor.core import AgnosticDatabase
from app.database import get_database

router = APIRouter(prefix="/api/news", tags=["news"])

@router.get("/")
async def get_news(db: AgnosticDatabase = Depends(get_database)):
    # Здесь можно получать новости из БД или возвращать статические данные
    return [
        {"title": "Новые поступления iPhone 15", "date": "2025-07-20"},
        {"title": "Акция на ремонт техники", "date": "2025-07-15"}
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    ]