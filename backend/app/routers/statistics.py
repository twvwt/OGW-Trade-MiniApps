<<<<<<< HEAD
from fastapi import APIRouter, Depends, Query
from motor.core import AgnosticDatabase
from app.database import get_database
from datetime import datetime, timedelta
from typing import Literal

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/")
async def get_statistics(
    period: Literal["day", "week", "month"] = Query("day"),
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение статистики продаж"""
    end_date = datetime.now()
    
    if period == "day":
        start_date = end_date - timedelta(days=1)
        group_format = "%H:00"
    elif period == "week":
        start_date = end_date - timedelta(days=7)
        group_format = "%Y-%m-%d"
    else:  # month
        start_date = end_date - timedelta(days=30)
        group_format = "%Y-%m-%d"
    
    # Статистика по дням/часам
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": "Отменен"}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": group_format,
                        "date": "$created_at"
                    }
                },
                "total_sales": {"$sum": "$total"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    sales_data = await db.orders.aggregate(pipeline).to_list(None)
    
    # Топ товаров
    top_products = await db.orders.aggregate([
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": "Отменен"}
            }
        },
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_name",
                "count": {"$sum": "$items.quantity"},
                "total": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(None)
    
    # Общая статистика
    total_stats = await db.orders.aggregate([
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": "Отменен"}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_sales": {"$sum": "$total"},
                "total_orders": {"$sum": 1},
                "avg_order": {"$avg": "$total"}
            }
        }
    ]).to_list(None)
    
    return {
        "sales_chart": {
            "labels": [item["_id"] for item in sales_data],
            "values": [item["total_sales"] for item in sales_data]
        },
        "top_products": {
            "labels": [item["_id"] for item in top_products],
            "values": [item["count"] for item in top_products]
        },
        "total_sales": total_stats[0]["total_sales"] if total_stats else 0,
        "total_orders": total_stats[0]["total_orders"] if total_stats else 0,
        "average_order": total_stats[0]["avg_order"] if total_stats else 0
=======
from fastapi import APIRouter, Depends, Query
from motor.core import AgnosticDatabase
from app.database import get_database
from datetime import datetime, timedelta
from typing import Literal

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

@router.get("/")
async def get_statistics(
    period: Literal["day", "week", "month"] = Query("day"),
    db: AgnosticDatabase = Depends(get_database)
):
    """Получение статистики продаж"""
    end_date = datetime.now()
    
    if period == "day":
        start_date = end_date - timedelta(days=1)
        group_format = "%H:00"
    elif period == "week":
        start_date = end_date - timedelta(days=7)
        group_format = "%Y-%m-%d"
    else:  # month
        start_date = end_date - timedelta(days=30)
        group_format = "%Y-%m-%d"
    
    # Статистика по дням/часам
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": "Отменен"}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": group_format,
                        "date": "$created_at"
                    }
                },
                "total_sales": {"$sum": "$total"},
                "count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    sales_data = await db.orders.aggregate(pipeline).to_list(None)
    
    # Топ товаров
    top_products = await db.orders.aggregate([
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": "Отменен"}
            }
        },
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_name",
                "count": {"$sum": "$items.quantity"},
                "total": {"$sum": {"$multiply": ["$items.price", "$items.quantity"]}}
            }
        },
        {"$sort": {"count": -1}},
        {"$limit": 5}
    ]).to_list(None)
    
    # Общая статистика
    total_stats = await db.orders.aggregate([
        {
            "$match": {
                "created_at": {"$gte": start_date, "$lte": end_date},
                "status": {"$ne": "Отменен"}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_sales": {"$sum": "$total"},
                "total_orders": {"$sum": 1},
                "avg_order": {"$avg": "$total"}
            }
        }
    ]).to_list(None)
    
    return {
        "sales_chart": {
            "labels": [item["_id"] for item in sales_data],
            "values": [item["total_sales"] for item in sales_data]
        },
        "top_products": {
            "labels": [item["_id"] for item in top_products],
            "values": [item["count"] for item in top_products]
        },
        "total_sales": total_stats[0]["total_sales"] if total_stats else 0,
        "total_orders": total_stats[0]["total_orders"] if total_stats else 0,
        "average_order": total_stats[0]["avg_order"] if total_stats else 0
>>>>>>> 134c63ca506067908136bfb1f963410f464c349a
    }