<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.core import AgnosticDatabase
from app.database import get_database
from app.models import Product
from app.schemas import ProductCreate
from typing import Optional  # Добавлен импорт
import os
import json
from urllib.parse import parse_qs
from fastapi import UploadFile, File
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])

async def verify_telegram_admin(request: Request, require_superadmin: bool = False):
    """Проверка прав администратора через Telegram InitData"""
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        return False
    
    try:
        data = parse_qs(init_data)
        user = json.loads(data['user'][0])
        user_id = user.get("id")
        
        db = await get_database()
        if user_id == int(os.getenv("SUPERADMIN_ID", 0)):
            return True
        
        if require_superadmin:
            return False
            
        return await db.admins.find_one({"user_id": user_id}) is not None
    except Exception:
        return False

@router.post("/products")
async def create_product(
    product: ProductCreate,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    if not await verify_telegram_admin(request):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        product_data = product.dict()
        result = await db.products.insert_one(product_data)
        return {"product_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    if not await verify_telegram_admin(request, require_superadmin=True):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        from bson import ObjectId
        result = await db.products.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/upload-price")
async def upload_price_file(
    file: UploadFile = File(...),
    request: Request = None,
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        # Создаем папку uploads, если ее нет
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Сохраняем файл
        file_path = upload_dir / "price.xlsx"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Запускаем импорт данных
        import subprocess
        result = subprocess.run(
            ["python", "import_data.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при импорте данных: {result.stderr}"
            )
        
        return {
            "status": "success",
            "message": "Файл успешно загружен и данные импортированы",
            "output": result.stdout
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке файла: {str(e)}"
=======
from fastapi import APIRouter, Depends, HTTPException, Request
from motor.core import AgnosticDatabase
from app.database import get_database
from app.models import Product
from app.schemas import ProductCreate
from typing import Optional  # Добавлен импорт
import os
import json
from urllib.parse import parse_qs
from fastapi import UploadFile, File
import shutil
import os
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"])

async def verify_telegram_admin(request: Request, require_superadmin: bool = False):
    """Проверка прав администратора через Telegram InitData"""
    init_data = request.headers.get("X-Telegram-Init-Data")
    if not init_data:
        return False
    
    try:
        data = parse_qs(init_data)
        user = json.loads(data['user'][0])
        user_id = user.get("id")
        
        db = await get_database()
        if user_id == int(os.getenv("SUPERADMIN_ID", 0)):
            return True
        
        if require_superadmin:
            return False
            
        return await db.admins.find_one({"user_id": user_id}) is not None
    except Exception:
        return False

@router.post("/products")
async def create_product(
    product: ProductCreate,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    if not await verify_telegram_admin(request):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        product_data = product.dict()
        result = await db.products.insert_one(product_data)
        return {"product_id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    request: Request,
    db: AgnosticDatabase = Depends(get_database)
):
    if not await verify_telegram_admin(request, require_superadmin=True):
        raise HTTPException(status_code=403, detail="Forbidden")
    
    try:
        from bson import ObjectId
        result = await db.products.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/upload-price")
async def upload_price_file(
    file: UploadFile = File(...),
    request: Request = None,
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        # Создаем папку uploads, если ее нет
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Сохраняем файл
        file_path = upload_dir / "price.xlsx"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Запускаем импорт данных
        import subprocess
        result = subprocess.run(
            ["python", "import_data.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при импорте данных: {result.stderr}"
            )
        
        return {
            "status": "success",
            "message": "Файл успешно загружен и данные импортированы",
            "output": result.stdout
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при загрузке файла: {str(e)}"
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
        )