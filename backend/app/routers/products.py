<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticDatabase
from app.database import get_database
from app.models import Product, PyObjectId
from app.schemas import ProductCreate, ProductResponse
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/api", tags=["products"])

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AgnosticDatabase = Depends(get_database)
):
    product_data = product.dict()
    try:
        result = await db.products.insert_one(product_data)
        return {"id": str(result.inserted_id), **product_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products/category")
async def get_categories(db: AgnosticDatabase = Depends(get_database)):
    try:
        pipeline = [
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "image": {"$first": "$photo1"}
            }},
            {"$project": {
                "name": "$_id",
                "product_count": "$count",
                "image": 1,
                "_id": 0
            }}
        ]
        
        categories = await db.products.aggregate(pipeline).to_list(None)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/subcategory")
async def get_subcategories(db: AgnosticDatabase = Depends(get_database)):
    try:
        pipeline = [
            {"$group": {
                "_id": {
                    "category": "$category",
                    "subcategory": "$subcategory"
                },
                "count": {"$sum": 1}
            }},
            {"$project": {
                "category": "$_id.category",
                "name": "$_id.subcategory",
                "product_count": "$count",
                "_id": 0
            }}
        ]
        
        subcategories = await db.products.aggregate(pipeline).to_list(None)
        return subcategories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products", response_model=List[Product])
async def get_products(
    category: str = None, 
    subcategory: str = None, 
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        query = {}
        if category:
            query["category"] = category
        if subcategory:
            query["subcategory"] = subcategory
        
        products = []
        async for product in db.products.find(query):
            try:
                # Преобразуем ObjectId в строку
                product["_id"] = str(product.get("_id", ""))
                
                # Обрабатываем пустую цену
                if 'price' in product and product['price'] == '':
                    product['price'] = None
                
                # Валидируем данные через модель Product
                validated_product = Product(**product)
                products.append(validated_product)
            except Exception as e:
                print(f"Ошибка при обработке продукта {product}: {e}")
                continue
                
        return products
    except Exception as e:
        print(f"Ошибка при запросе продуктов: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching products"
=======
from fastapi import APIRouter, Depends, HTTPException
from motor.core import AgnosticDatabase
from app.database import get_database
from app.models import Product, PyObjectId
from app.schemas import ProductCreate, ProductResponse
from typing import List
from bson import ObjectId

router = APIRouter(prefix="/api", tags=["products"])

@router.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate, 
    db: AgnosticDatabase = Depends(get_database)
):
    product_data = product.dict()
    try:
        result = await db.products.insert_one(product_data)
        return {"id": str(result.inserted_id), **product_data}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/products/category")
async def get_categories(db: AgnosticDatabase = Depends(get_database)):
    try:
        pipeline = [
            {"$group": {
                "_id": "$category",
                "count": {"$sum": 1},
                "image": {"$first": "$photo1"}
            }},
            {"$project": {
                "name": "$_id",
                "product_count": "$count",
                "image": 1,
                "_id": 0
            }}
        ]
        
        categories = await db.products.aggregate(pipeline).to_list(None)
        return categories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products/subcategory")
async def get_subcategories(db: AgnosticDatabase = Depends(get_database)):
    try:
        pipeline = [
            {"$group": {
                "_id": {
                    "category": "$category",
                    "subcategory": "$subcategory"
                },
                "count": {"$sum": 1}
            }},
            {"$project": {
                "category": "$_id.category",
                "name": "$_id.subcategory",
                "product_count": "$count",
                "_id": 0
            }}
        ]
        
        subcategories = await db.products.aggregate(pipeline).to_list(None)
        return subcategories
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/products", response_model=List[Product])
async def get_products(
    category: str = None, 
    subcategory: str = None, 
    db: AgnosticDatabase = Depends(get_database)
):
    try:
        query = {}
        if category:
            query["category"] = category
        if subcategory:
            query["subcategory"] = subcategory
        
        products = []
        async for product in db.products.find(query):
            try:
                # Преобразуем ObjectId в строку
                product["_id"] = str(product.get("_id", ""))
                
                # Обрабатываем пустую цену
                if 'price' in product and product['price'] == '':
                    product['price'] = None
                
                # Валидируем данные через модель Product
                validated_product = Product(**product)
                products.append(validated_product)
            except Exception as e:
                print(f"Ошибка при обработке продукта {product}: {e}")
                continue
                
        return products
    except Exception as e:
        print(f"Ошибка при запросе продуктов: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error while fetching products"
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
        )