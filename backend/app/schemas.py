<<<<<<< HEAD
from typing import Optional, List
from pydantic import BaseModel

class ProductCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    product_name: str
    color: str
    storage: str
    country: Optional[str] = None
    short_description: str = ""
    specifications: str = ""
    price: float
    configuration: Optional[str] = None
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    category: str
    subcategory: Optional[str] = None
    product_name: str
    color: str
    storage: str
    country: Optional[str] = None
    short_description: str = ""
    specifications: str = ""
    price: float
    configuration: Optional[str] = None
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
    
    class Config:
        json_encoders = {
            "id": str
        }
    
class CategoryResponse(BaseModel):
    name: str
    image: Optional[str] = None
    product_count: int

class OrderCreate(BaseModel):
    items: List[dict]
    total: float
    user_id: Optional[str] = None  # Будет установлен из Telegram данных++
    
class SubcategoryResponse(BaseModel):
    category: str
    name: str
    product_count: int
    
class UserCreate(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class CartUpdate(BaseModel):
    product_id: str
    quantity: int = 1

class FavoriteUpdate(BaseModel):
    product_id: str

class ProductVariant(BaseModel):
    color: str
    storage: str
    price: float
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
=======
from typing import Optional, List
from pydantic import BaseModel

class ProductCreate(BaseModel):
    category: str
    subcategory: Optional[str] = None
    product_name: str
    color: str
    storage: str
    country: Optional[str] = None
    short_description: str = ""
    specifications: str = ""
    price: float
    configuration: Optional[str] = None
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None

class ProductResponse(BaseModel):
    id: str
    category: str
    subcategory: Optional[str] = None
    product_name: str
    color: str
    storage: str
    country: Optional[str] = None
    short_description: str = ""
    specifications: str = ""
    price: float
    configuration: Optional[str] = None
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
    
    class Config:
        json_encoders = {
            "id": str
        }
    
class CategoryResponse(BaseModel):
    name: str
    image: Optional[str] = None
    product_count: int

class OrderCreate(BaseModel):
    items: List[dict]
    total: float
    user_id: Optional[str] = None  # Будет установлен из Telegram данных++
    
class SubcategoryResponse(BaseModel):
    category: str
    name: str
    product_count: int
    
class UserCreate(BaseModel):
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class CartUpdate(BaseModel):
    product_id: str
    quantity: int = 1

class FavoriteUpdate(BaseModel):
    product_id: str

class ProductVariant(BaseModel):
    color: str
    storage: str
    price: float
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    configuration: Optional[str] = None