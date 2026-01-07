import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings, setup_logging
from app.database.mongodb import close_mongodb, init_mongodb
from app.database.postgres import init_db
from app.routers import auth, customers, invoices, products

setup_logging()
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting CRM Application...")

    try:
        init_db()
        logger.info("PostgreSQL initialized")
    except Exception as e:
        logger.error(f"Failed to initialize PostgreSQL: {e}")
        raise

    try:
        init_mongodb()
        logger.info("MongoDB initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        raise

    logger.info("CRM Application started successfully")
    yield

    logger.info("Shutting down CRM Application...")
    close_mongodb()
    logger.info("CRM Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    description="Production-grade CRM Application with FastAPI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(invoices.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Welcome to CRM Application API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
