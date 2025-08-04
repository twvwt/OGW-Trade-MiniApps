<<<<<<< HEAD
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from typing import Optional, Any, List
from datetime import datetime
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    category: str
    subcategory: Optional[str] = None
    product_name: str
    color: str
    storage: str
    country: Optional[str] = None
    short_description: str = ""
    specifications: str = ""
    price: Optional[float] = None  # Изменено на Optional[float] и значение по умолчанию None
    configuration: Optional[str] = None
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    variants: Optional[List[dict]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "category": "smartphones",
                "subcategory": "flagship",
                "product_name": "Example Phone",
                "price": 999.99,
                "color": "black",
                "storage": "256GB",
                "configuration": "8GB RAM"
            }
        }
    )
    
class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: int  # Telegram user ID
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    delivery_preference: Optional[str] = None
    payment_preference: Optional[str] = None
    cart: List[dict] = Field(default_factory=list)
    favorites: List[PyObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    telegram_data: Optional[dict] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class CartItem(BaseModel):
    product_id: PyObjectId
    quantity: int = 1
    selected: bool = True

class FavoriteItem(BaseModel):
    product_id: PyObjectId
    added_at: datetime = Field(default_factory=datetime.now)
    
class Order(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str  # Telegram user ID или "anonymous"
    user_info: Optional[dict] = None
    items: List[dict]
    customer: dict
    delivery_method: str
    payment_method: str
    comment: Optional[str] = None
    total: float
    status: str = "new"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
=======
from pydantic import BaseModel, Field, ConfigDict
from bson import ObjectId
from typing import Optional, Any, List
from datetime import datetime
from pydantic_core import core_schema


class PyObjectId(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, _source_type: Any, _handler: Any) -> core_schema.CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.str_schema(),
            serialization=core_schema.to_string_ser_schema(),
        )

    @classmethod
    def validate(cls, v: Any) -> str:
        if isinstance(v, ObjectId):
            return str(v)
        if isinstance(v, str) and ObjectId.is_valid(v):
            return v
        raise ValueError("Invalid ObjectId")
    
class Product(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    category: str
    subcategory: Optional[str] = None
    product_name: str
    color: str
    storage: str
    country: Optional[str] = None
    short_description: str = ""
    specifications: str = ""
    price: Optional[float] = None  # Изменено на Optional[float] и значение по умолчанию None
    configuration: Optional[str] = None
    photo1: Optional[str] = None
    photo2: Optional[str] = None
    photo3: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    variants: Optional[List[dict]] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "category": "smartphones",
                "subcategory": "flagship",
                "product_name": "Example Phone",
                "price": 999.99,
                "color": "black",
                "storage": "256GB",
                "configuration": "8GB RAM"
            }
        }
    )
    
class User(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: int  # Telegram user ID
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    photo_url: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    delivery_preference: Optional[str] = None
    payment_preference: Optional[str] = None
    cart: List[dict] = Field(default_factory=list)
    favorites: List[PyObjectId] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    last_activity: datetime = Field(default_factory=datetime.now)
    telegram_data: Optional[dict] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class CartItem(BaseModel):
    product_id: PyObjectId
    quantity: int = 1
    selected: bool = True

class FavoriteItem(BaseModel):
    product_id: PyObjectId
    added_at: datetime = Field(default_factory=datetime.now)
    
class Order(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    user_id: str  # Telegram user ID или "anonymous"
    user_info: Optional[dict] = None
    items: List[dict]
    customer: dict
    delivery_method: str
    payment_method: str
    comment: Optional[str] = None
    total: float
    status: str = "new"
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    )