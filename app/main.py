# app/main.py
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import health, kyc
from app.config import APP_ENV
from app.core import risk_scorer, sanctions_screener
from app.db.database import init_db
from app.streaming.consumer import start_consumer, stop_consumer
from app.streaming.producer import initialise_producer, shutdown_producer

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting KYC Platform | env={APP_ENV}")

    init_db()
    logger.info("✅ PostgreSQL tables ready")

    screening_ok = sanctions_screener.load_screening_lists()
    logger.info(f"{'✅' if screening_ok else '⚠️ '} Screening lists loaded")

    model_ok = risk_scorer.load_model()
    logger.info(f"{'✅' if model_ok else '⚠️ '} Risk model loaded")

    initialise_producer()
    start_consumer()
    logger.info("🚀 KYC Platform ready")

    yield

    stop_consumer()
    shutdown_producer()


app = FastAPI(title="KYC & Identity Risk Intelligence Platform", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(health.router)
app.include_router(kyc.router, prefix="/api/v1")