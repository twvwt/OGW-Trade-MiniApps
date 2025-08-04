<<<<<<< HEAD
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from fastapi import HTTPException
import os
from typing import Optional
from datetime import datetime  # Упростили импорт

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "OGW")
SUPERADMIN_ID = int(os.getenv("SUPERADMIN_ID", 0))

client: Optional[AsyncIOMotorClient] = None
db = None

async def init_db():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        await client.admin.command('ping')
        
        collections = await db.list_collection_names()
        required_collections = ['products', 'orders', 'admins', 'users']
        
        for coll in required_collections:
            if coll not in collections:
                await db.create_collection(coll)
        
        # Create indexes
        await db.products.create_index([("category", 1)])
        await db.products.create_index([("subcategory", 1)])
        await db.admins.create_index([("user_id", 1)], unique=True)
        await db.users.create_index([("user_id", 1)], unique=True)
        await db.orders.create_index([("user_id", 1)])  # Добавлен индекс для заказов
        
        if SUPERADMIN_ID:
            await db.admins.update_one(
                {"user_id": SUPERADMIN_ID},
                {"$setOnInsert": {"is_superadmin": True, "created_at": datetime.now()}},
                upsert=True
            )
        if 'orders' not in await db.list_collection_names():
            await db.create_collection('orders')
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

async def get_database():
    if db is None:
        await init_db()
    try:
        await client.admin.command('ping')
        return db
    except Exception as e:
        print(f"Database connection error: {e}")
        await init_db()  # Попробуем переподключиться
        return db

async def close_db():
    if client:
        client.close()
        
async def get_user_by_telegram_id(user_id: int):
    db = await get_database()
    return await db.users.find_one({"user_id": user_id})

async def create_or_update_user(user_data: dict):
    db = await get_database()
    user_data["last_activity"] = datetime.now()
    result = await db.users.update_one(
        {"user_id": user_data["user_id"]},
        {"$set": user_data, "$setOnInsert": {"created_at": datetime.now()}},
        upsert=True
    )
    return result
=======
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from fastapi import HTTPException
import os
from typing import Optional
from datetime import datetime  # Упростили импорт

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "OGW")
SUPERADMIN_ID = int(os.getenv("SUPERADMIN_ID", 0))

client: Optional[AsyncIOMotorClient] = None
db = None

async def init_db():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        
        await client.admin.command('ping')
        
        collections = await db.list_collection_names()
        required_collections = ['products', 'orders', 'admins', 'users']
        
        for coll in required_collections:
            if coll not in collections:
                await db.create_collection(coll)
        
        # Create indexes
        await db.products.create_index([("category", 1)])
        await db.products.create_index([("subcategory", 1)])
        await db.admins.create_index([("user_id", 1)], unique=True)
        await db.users.create_index([("user_id", 1)], unique=True)
        await db.orders.create_index([("user_id", 1)])  # Добавлен индекс для заказов
        
        if SUPERADMIN_ID:
            await db.admins.update_one(
                {"user_id": SUPERADMIN_ID},
                {"$setOnInsert": {"is_superadmin": True, "created_at": datetime.now()}},
                upsert=True
            )
        if 'orders' not in await db.list_collection_names():
            await db.create_collection('orders')
            
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        raise

async def get_database():
    if db is None:
        await init_db()
    try:
        await client.admin.command('ping')
        return db
    except Exception as e:
        print(f"Database connection error: {e}")
        await init_db()  # Попробуем переподключиться
        return db

async def close_db():
    if client:
        client.close()
        
async def get_user_by_telegram_id(user_id: int):
    db = await get_database()
    return await db.users.find_one({"user_id": user_id})

async def create_or_update_user(user_data: dict):
    db = await get_database()
    user_data["last_activity"] = datetime.now()
    result = await db.users.update_one(
        {"user_id": user_data["user_id"]},
        {"$set": user_data, "$setOnInsert": {"created_at": datetime.now()}},
        upsert=True
    )
    return result
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
