import logging

from pymongo import MongoClient
from pymongo.database import Database

from app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

_client: MongoClient | None = None
_db: Database | None = None


def get_mongodb_client() -> MongoClient:
    global _client
    if _client is None:
        logger.info(f"Connecting to MongoDB at {settings.mongodb_host}:{settings.mongodb_port}")
        _client = MongoClient(settings.mongodb_url)
    return _client


def get_mongodb() -> Database:
    global _db
    if _db is None:
        client = get_mongodb_client()
        _db = client[settings.mongodb_db]
    return _db


def init_mongodb() -> None:
    logger.info("Initializing MongoDB database...")
    db = get_mongodb()

    if "roles" not in db.list_collection_names():
        db.create_collection("roles")
        logger.info("Created 'roles' collection")

    if "users" not in db.list_collection_names():
        db.create_collection("users")
        logger.info("Created 'users' collection")

    if "permissions" not in db.list_collection_names():
        db.create_collection("permissions")
        logger.info("Created 'permissions' collection")

    db.users.create_index("email", unique=True)
    db.users.create_index("username", unique=True)
    db.roles.create_index("name", unique=True)

    _seed_roles_and_permissions(db)

    logger.info("MongoDB database initialized successfully")


def _seed_roles_and_permissions(db: Database) -> None:
    roles_data = [
        {
            "name": "admin",
            "description": "Full system access",
            "permissions": ["all"],
        },
        {
            "name": "manager",
            "description": "Manage customers, products, and invoices",
            "permissions": [
                "customers:read", "customers:write", "customers:delete",
                "products:read", "products:write", "products:delete",
                "invoices:read", "invoices:write", "invoices:delete",
            ],
        },
        {
            "name": "staff",
            "description": "Create invoices and view data",
            "permissions": [
                "customers:read",
                "products:read",
                "invoices:read", "invoices:write",
            ],
        },
        {
            "name": "viewer",
            "description": "Read-only access",
            "permissions": [
                "customers:read",
                "products:read",
                "invoices:read",
            ],
        },
    ]

    for role_data in roles_data:
        existing = db.roles.find_one({"name": role_data["name"]})
        if not existing:
            db.roles.insert_one(role_data)
            logger.info(f"Created role: {role_data['name']}")
        else:
            logger.info(f"Role already exists: {role_data['name']}")


def close_mongodb() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None
        logger.info("MongoDB connection closed")
