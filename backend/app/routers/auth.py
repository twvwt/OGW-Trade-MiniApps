<<<<<<< HEAD
# auth.py (полностью обновленный)
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import json
from urllib.parse import parse_qs
from app.database import get_user_by_telegram_id, create_or_update_user
from app.models import User
import os
router = APIRouter(prefix="/auth", tags=["auth"])

# Конфигурация - используйте переменные окружения в продакшене
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

class TelegramAuthData(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram auth data required"
        )
    
    try:
        # В реальном приложении нужно проверять хэш данных
        data = parse_qs(init_data)
        user_data = json.loads(data['user'][0])
        
        user = await get_user_by_telegram_id(user_data['id'])
        if not user:
            # Создаем нового пользователя
            user = {
                "user_id": user_data['id'],
                "username": user_data.get('username'),
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "photo_url": user_data.get('photo_url'),
                "telegram_data": user_data
            }
            await create_or_update_user(user)
            user = await get_user_by_telegram_id(user_data['id'])
        
        return User(**user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram auth data"
        )

@router.post("/telegram", response_model=Token)
async def login_with_telegram(request: Request):
    user = await get_current_user(request)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
    
@router.get("/me", response_model=User)
async def read_users_me(user: User = Depends(get_current_user)):
=======
# auth.py (полностью обновленный)
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import jwt
import json
from urllib.parse import parse_qs
from app.database import get_user_by_telegram_id, create_or_update_user
from app.models import User
import os
router = APIRouter(prefix="/auth", tags=["auth"])

# Конфигурация - используйте переменные окружения в продакшене
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

class TelegramAuthData(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    photo_url: Optional[str] = None
    auth_date: int
    hash: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request):
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Telegram auth data required"
        )
    
    try:
        # В реальном приложении нужно проверять хэш данных
        data = parse_qs(init_data)
        user_data = json.loads(data['user'][0])
        
        user = await get_user_by_telegram_id(user_data['id'])
        if not user:
            # Создаем нового пользователя
            user = {
                "user_id": user_data['id'],
                "username": user_data.get('username'),
                "first_name": user_data.get('first_name'),
                "last_name": user_data.get('last_name'),
                "photo_url": user_data.get('photo_url'),
                "telegram_data": user_data
            }
            await create_or_update_user(user)
            user = await get_user_by_telegram_id(user_data['id'])
        
        return User(**user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram auth data"
        )

@router.post("/telegram", response_model=Token)
async def login_with_telegram(request: Request):
    user = await get_current_user(request)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id)},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }
    
@router.get("/me", response_model=User)
async def read_users_me(user: User = Depends(get_current_user)):
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    return user