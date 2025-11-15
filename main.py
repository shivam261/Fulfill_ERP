import os
from fastapi import FastAPI, Response
from contextlib import asynccontextmanager

from orjson import dumps
from dotenv import load_dotenv 
import logging
from src.database import create_db_and_tables, get_session
from src.upstash_redis import init_upstash_redis  # Import Upstash Redis function
from src.auth.router import router as auth_router
from src.products.router import router as products_router
from src.webhooks.router import router as webhooks_router
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Starting up...")
    logger.info("Creating database and tables...")
    await create_db_and_tables()
    logger.info("Initializing Upstash Redis...")
    init_upstash_redis()       # Initialize Upstash Redis connection
    yield                        # app runs here
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)


app.include_router(auth_router)
app.include_router(products_router)
app.include_router(webhooks_router)
@app.get("/")
async def root():
    return {"message": "Hello World"}