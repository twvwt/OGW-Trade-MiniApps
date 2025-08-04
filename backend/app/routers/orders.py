<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from motor.core import AgnosticDatabase
from app.database import get_database
from datetime import datetime, timedelta
from pydantic import BaseModel, validator, Field
from typing import List, Optional
from bson import ObjectId
import json
from urllib.parse import parse_qs
from app.models import Order  # Добавлен импорт модели Order
import os
import httpx
import asyncio
router = APIRouter(prefix="/api/orders", tags=["orders"])

async def notify_telegram_bot(order_data: dict):
    """Отправляет уведомление в Telegram бот"""
    try:
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            return
            
        # Здесь можно либо напрямую вызывать бота, либо через webhook
        async with httpx.AsyncClient() as client:
            await client.post(
                f"http://localhost:8001/notify_order",  # URL вашего бота
                json=order_data,
                timeout=10
            )
    except Exception as e:
        print(f"Ошибка при отправке уведомления в бота: {e}")
        
        
class OrderItem(BaseModel):
    product_id: str = Field(..., min_length=1, description="ID товара")
    product_name: str = Field(..., min_length=1, description="Название товара")
    price: float = Field(..., gt=0, description="Цена за единицу")
    quantity: int = Field(..., gt=0, description="Количество")
    image_url: Optional[str] = Field(None, description="URL изображения товара")

class CustomerAddress(BaseModel):
    city: str = Field(..., min_length=2, description="Город")
    street: str = Field(..., min_length=2, description="Улица")
    house: str = Field(..., min_length=1, description="Дом")
    apartment: Optional[str] = Field(None, description="Квартира")

class CustomerInfo(BaseModel):
    first_name: str = Field(..., min_length=2, description="Имя")
    last_name: str = Field(..., min_length=2, description="Фамилия")
    phone: str = Field(..., min_length=5, description="Телефон")
    email: Optional[str] = Field(None, description="Email")
    address: CustomerAddress

class OrderCreate(BaseModel):
    items: List[OrderItem]
    customer: CustomerInfo
    delivery_method: str = Field(..., min_length=1, description="Способ доставки")
    payment_method: str = Field(..., min_length=1, description="Способ оплаты")
    comment: Optional[str] = Field(None, description="Комментарий")
    total: float = Field(..., gt=0, description="Общая сумма")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError("Заказ должен содержать хотя бы один товар")
        return v

async def get_telegram_user(request: Request):
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        return None
    
    try:
        data = parse_qs(init_data)
        return json.loads(data['user'][0])
    except Exception:
        return None
class UpdateOrderStatus(BaseModel):
    status: str

@router.get("")
async def get_orders(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение списка заказов с фильтрами"""
    query = {}
    
    if status and status != "all":
        query["status"] = status
    
    if date_from and date_to:
        try:
            start_date = datetime.fromisoformat(date_from)
            end_date = datetime.fromisoformat(date_to) + timedelta(days=1)
            query["created_at"] = {"$gte": start_date, "$lte": end_date}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    orders = []
    async for order in db.orders.find(query).sort("created_at", -1):
        order["_id"] = str(order["_id"])
        orders.append(order)
    
    return orders

@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение деталей конкретного заказа"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order["_id"] = str(order["_id"])
        return order
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: UpdateOrderStatus,
    db: AgnosticDatabase = Depends(get_database)
):
    """Обновление статуса заказа"""
    valid_statuses = ["Новый", "Подтвержден", "Отменен", "Выполнен"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    try:
        result = await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "status": status_data.status,
                "updated_at": datetime.now()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"status": "updated"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        # Получаем данные пользователя
        user = await get_telegram_user(request)
        user_id = str(user['id']) if user else "anonymous"
        
        # Формируем документ для MongoDB
        order_doc = {
            "user_id": user_id,
            "user_info": {
                "telegram_id": user_id,
                "username": user.get('username'),
                "first_name": user.get('first_name'),
                "last_name": user.get('last_name')
            } if user else None,
            "items": [item.dict() for item in order_data.items],
            "customer": order_data.customer.dict(),
            "delivery_method": order_data.delivery_method,
            "payment_method": order_data.payment_method,
            "comment": order_data.comment,
            "total": order_data.total,
            "status": "new",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Вставляем заказ в коллекцию orders
        result = await db.orders.insert_one(order_doc)
        created_order = await db.orders.find_one({"_id": result.inserted_id})
        
        # Отправляем уведомление
        asyncio.create_task(notify_telegram_bot(created_order))
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось создать заказ"
            )
        
        # Обновляем статистику товаров
        for item in order_data.items:
            await db.products.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$inc": {"sales_count": item.quantity}}
            )
        
        return {
            "order_id": str(result.inserted_id),
            "status": "created",
            "total": order_data.total
        }
        
    except Exception as e:
        print(f"Ошибка при создании заказа: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )

@router.get("/{order_id}")
async def get_order_status(
    order_id: str,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )
        
        return {
            "order_id": order_id,
            "status": order.get("status", "unknown"),
            "total": order.get("total", 0),
            "created_at": order.get("created_at")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при получении заказа: {str(e)}"
        )
        
@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение деталей конкретного заказа"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Преобразуем ObjectId в строку
        order["_id"] = str(order["_id"])
        
        # Преобразуем ObjectId в товарах, если они есть
        if "items" in order:
            for item in order["items"]:
                if isinstance(item.get("product_id"), ObjectId):
                    item["product_id"] = str(item["product_id"])
        
        return order
    except Exception as e:
=======
from fastapi import APIRouter, Depends, HTTPException, Request, status, Query
from motor.core import AgnosticDatabase
from app.database import get_database
from datetime import datetime, timedelta
from pydantic import BaseModel, validator, Field
from typing import List, Optional
from bson import ObjectId
import json
from urllib.parse import parse_qs
from app.models import Order  # Добавлен импорт модели Order
import os
import httpx
import asyncio
router = APIRouter(prefix="/api/orders", tags=["orders"])

async def notify_telegram_bot(order_data: dict):
    """Отправляет уведомление в Telegram бот"""
    try:
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            return
            
        # Здесь можно либо напрямую вызывать бота, либо через webhook
        async with httpx.AsyncClient() as client:
            await client.post(
                f"http://localhost:8001/notify_order",  # URL вашего бота
                json=order_data,
                timeout=10
            )
    except Exception as e:
        print(f"Ошибка при отправке уведомления в бота: {e}")
        
        
class OrderItem(BaseModel):
    product_id: str = Field(..., min_length=1, description="ID товара")
    product_name: str = Field(..., min_length=1, description="Название товара")
    price: float = Field(..., gt=0, description="Цена за единицу")
    quantity: int = Field(..., gt=0, description="Количество")
    image_url: Optional[str] = Field(None, description="URL изображения товара")

class CustomerAddress(BaseModel):
    city: str = Field(..., min_length=2, description="Город")
    street: str = Field(..., min_length=2, description="Улица")
    house: str = Field(..., min_length=1, description="Дом")
    apartment: Optional[str] = Field(None, description="Квартира")

class CustomerInfo(BaseModel):
    first_name: str = Field(..., min_length=2, description="Имя")
    last_name: str = Field(..., min_length=2, description="Фамилия")
    phone: str = Field(..., min_length=5, description="Телефон")
    email: Optional[str] = Field(None, description="Email")
    address: CustomerAddress

class OrderCreate(BaseModel):
    items: List[OrderItem]
    customer: CustomerInfo
    delivery_method: str = Field(..., min_length=1, description="Способ доставки")
    payment_method: str = Field(..., min_length=1, description="Способ оплаты")
    comment: Optional[str] = Field(None, description="Комментарий")
    total: float = Field(..., gt=0, description="Общая сумма")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError("Заказ должен содержать хотя бы один товар")
        return v

async def get_telegram_user(request: Request):
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        return None
    
    try:
        data = parse_qs(init_data)
        return json.loads(data['user'][0])
    except Exception:
        return None
class UpdateOrderStatus(BaseModel):
    status: str

@router.get("")
async def get_orders(
    status: Optional[str] = Query(None),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение списка заказов с фильтрами"""
    query = {}
    
    if status and status != "all":
        query["status"] = status
    
    if date_from and date_to:
        try:
            start_date = datetime.fromisoformat(date_from)
            end_date = datetime.fromisoformat(date_to) + timedelta(days=1)
            query["created_at"] = {"$gte": start_date, "$lte": end_date}
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")
    
    orders = []
    async for order in db.orders.find(query).sort("created_at", -1):
        order["_id"] = str(order["_id"])
        orders.append(order)
    
    return orders

@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение деталей конкретного заказа"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order["_id"] = str(order["_id"])
        return order
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")

@router.put("/{order_id}/status")
async def update_order_status(
    order_id: str,
    status_data: UpdateOrderStatus,
    db: AgnosticDatabase = Depends(get_database)
):
    """Обновление статуса заказа"""
    valid_statuses = ["Новый", "Подтвержден", "Отменен", "Выполнен"]
    if status_data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    try:
        result = await db.orders.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {
                "status": status_data.status,
                "updated_at": datetime.now()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"status": "updated"}
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
@router.post("", status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        # Получаем данные пользователя
        user = await get_telegram_user(request)
        user_id = str(user['id']) if user else "anonymous"
        
        # Формируем документ для MongoDB
        order_doc = {
            "user_id": user_id,
            "user_info": {
                "telegram_id": user_id,
                "username": user.get('username'),
                "first_name": user.get('first_name'),
                "last_name": user.get('last_name')
            } if user else None,
            "items": [item.dict() for item in order_data.items],
            "customer": order_data.customer.dict(),
            "delivery_method": order_data.delivery_method,
            "payment_method": order_data.payment_method,
            "comment": order_data.comment,
            "total": order_data.total,
            "status": "new",
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Вставляем заказ в коллекцию orders
        result = await db.orders.insert_one(order_doc)
        created_order = await db.orders.find_one({"_id": result.inserted_id})
        
        # Отправляем уведомление
        asyncio.create_task(notify_telegram_bot(created_order))
        
        if not result.inserted_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Не удалось создать заказ"
            )
        
        # Обновляем статистику товаров
        for item in order_data.items:
            await db.products.update_one(
                {"_id": ObjectId(item.product_id)},
                {"$inc": {"sales_count": item.quantity}}
            )
        
        return {
            "order_id": str(result.inserted_id),
            "status": "created",
            "total": order_data.total
        }
        
    except Exception as e:
        print(f"Ошибка при создании заказа: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )

@router.get("/{order_id}")
async def get_order_status(
    order_id: str,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Заказ не найден"
            )
        
        return {
            "order_id": order_id,
            "status": order.get("status", "unknown"),
            "total": order.get("total", 0),
            "created_at": order.get("created_at")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ошибка при получении заказа: {str(e)}"
        )
        
@router.get("/{order_id}")
async def get_order_details(
    order_id: str,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение деталей конкретного заказа"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        # Преобразуем ObjectId в строку
        order["_id"] = str(order["_id"])
        
        # Преобразуем ObjectId в товарах, если они есть
        if "items" in order:
            for item in order["items"]:
                if isinstance(item.get("product_id"), ObjectId):
                    item["product_id"] = str(item["product_id"])
        
        return order
    except Exception as e:
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
        raise HTTPException(status_code=400, detail="Invalid order ID")