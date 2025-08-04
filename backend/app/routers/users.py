<<<<<<< HEAD
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_database, get_user_by_telegram_id, create_or_update_user
from app.models import User, Product
from app.schemas import FavoriteUpdate  # Import FavoriteUpdate from schemas
from app.routers.auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List
import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/users", tags=["users"])

class UpdateUserProfile(BaseModel):
    address: Optional[str] = None
    phone: Optional[str] = None
    delivery_preference: Optional[str] = None
    payment_preference: Optional[str] = None

@router.get("/me", response_model=User)
async def get_user_profile(user: User = Depends(get_current_user)):
    return user

@router.put("/me", response_model=User)
async def update_user_profile(
    profile_data: UpdateUserProfile,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    update_data = profile_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.datetime.now()
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": update_data}
    )
    
    updated_user = await get_user_by_telegram_id(user.user_id)
    return User(**updated_user)

@router.get("/favorites", response_model=List[Product])
async def get_user_favorites(user: User = Depends(get_current_user)):
    db = await get_database()
    favorites = await db.products.find({
        "_id": {"$in": [ObjectId(id) for id in user.favorites]}
    }).to_list(None)
    return favorites

@router.post("/favorites")
async def add_to_favorites(
    item: FavoriteUpdate,
    user: User = Depends(get_current_user)
):
    db = await get_database()
    
    # Check if product exists
    product = await db.products.find_one({"_id": ObjectId(item.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product is already in favorites
    if ObjectId(item.product_id) in user.favorites:
        raise HTTPException(status_code=400, detail="Product already in favorites")
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$push": {"favorites": ObjectId(item.product_id)}}
    )
    
    return {"status": "success"}

@router.delete("/favorites/{product_id}")
async def remove_from_favorites(
    product_id: str,
    user: User = Depends(get_current_user)
):
    db = await get_database()
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$pull": {"favorites": ObjectId(product_id)}}
    )
    
=======
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_database, get_user_by_telegram_id, create_or_update_user
from app.models import User, Product
from app.schemas import FavoriteUpdate  # Import FavoriteUpdate from schemas
from app.routers.auth import get_current_user
from pydantic import BaseModel
from typing import Optional, List
import datetime
from bson import ObjectId

router = APIRouter(prefix="/api/users", tags=["users"])

class UpdateUserProfile(BaseModel):
    address: Optional[str] = None
    phone: Optional[str] = None
    delivery_preference: Optional[str] = None
    payment_preference: Optional[str] = None

@router.get("/me", response_model=User)
async def get_user_profile(user: User = Depends(get_current_user)):
    return user

@router.put("/me", response_model=User)
async def update_user_profile(
    profile_data: UpdateUserProfile,
    user: User = Depends(get_current_user),
    db = Depends(get_database)
):
    update_data = profile_data.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.datetime.now()
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$set": update_data}
    )
    
    updated_user = await get_user_by_telegram_id(user.user_id)
    return User(**updated_user)

@router.get("/favorites", response_model=List[Product])
async def get_user_favorites(user: User = Depends(get_current_user)):
    db = await get_database()
    favorites = await db.products.find({
        "_id": {"$in": [ObjectId(id) for id in user.favorites]}
    }).to_list(None)
    return favorites

@router.post("/favorites")
async def add_to_favorites(
    item: FavoriteUpdate,
    user: User = Depends(get_current_user)
):
    db = await get_database()
    
    # Check if product exists
    product = await db.products.find_one({"_id": ObjectId(item.product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Check if product is already in favorites
    if ObjectId(item.product_id) in user.favorites:
        raise HTTPException(status_code=400, detail="Product already in favorites")
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$push": {"favorites": ObjectId(item.product_id)}}
    )
    
    return {"status": "success"}

@router.delete("/favorites/{product_id}")
async def remove_from_favorites(
    product_id: str,
    user: User = Depends(get_current_user)
):
    db = await get_database()
    
    await db.users.update_one(
        {"user_id": user.user_id},
        {"$pull": {"favorites": ObjectId(product_id)}}
    )
    
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    return {"status": "success"}