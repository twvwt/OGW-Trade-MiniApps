<<<<<<< HEAD
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, orders, admin, news, auth, users, statistics
from app.database import init_db, close_db, get_database
from pymongo import ASCENDING

app = FastAPI(
    title="OGW Trade API",
    description="API для магазина электроники OGW Trade",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_telegram_data(request: Request, call_next):
    """Middleware для добавления данных Telegram в запрос"""
    if "X-Telegram-Init-Data" in request.headers:
        request.state.telegram_data = request.headers["X-Telegram-Init-Data"]
    response = await call_next(request)
    return response

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(news.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(statistics.router)

@app.on_event("startup")
async def startup_db_client():
    await init_db()
    db = await get_database()
    await db.products.create_index([("category", 1)])
    await db.products.create_index([("subcategory", 1)])

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to OGW Trade API"}
=======
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.routers import products, orders, admin, news, auth, users, statistics
from app.database import init_db, close_db, get_database
from pymongo import ASCENDING

app = FastAPI(
    title="OGW Trade API",
    description="API для магазина электроники OGW Trade",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.middleware("http")
async def add_telegram_data(request: Request, call_next):
    """Middleware для добавления данных Telegram в запрос"""
    if "X-Telegram-Init-Data" in request.headers:
        request.state.telegram_data = request.headers["X-Telegram-Init-Data"]
    response = await call_next(request)
    return response

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(news.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(statistics.router)

@app.on_event("startup")
async def startup_db_client():
    await init_db()
    db = await get_database()
    await db.products.create_index([("category", 1)])
    await db.products.create_index([("subcategory", 1)])

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_db()

@app.get("/")
async def root():
    return {"message": "Welcome to OGW Trade API"}
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
