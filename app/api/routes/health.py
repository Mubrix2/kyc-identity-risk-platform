# app/api/routes/health.py
from fastapi import APIRouter
from app.streaming.consumer import get_consumer_stats
from app.config import APP_ENV

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    consumer = get_consumer_stats()
    return {
        "status": "healthy", "env": APP_ENV,
        "consumer": {"running": consumer["running"], "consumed": consumer["consumed"]},
    }