import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from common.config import settings
from common.db import init_db
from api.routers import health, products, reviews

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Product Reviews API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(products.router)
app.include_router(reviews.router)


@app.on_event("startup")
def startup_event():
    init_db()
    logger.info(
        "Database initialized. Connecting to RabbitMQ at %s:%s queue=%s",
        settings.rabbit_host,
        settings.rabbit_port,
        settings.rabbit_queue,
    )
