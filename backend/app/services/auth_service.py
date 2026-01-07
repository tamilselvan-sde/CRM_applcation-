import logging
from datetime import datetime, timedelta
from typing import Optional

from bson import ObjectId
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings
from app.database.mongodb import get_mongodb
from app.schemas.user import TokenData, UserCreate

logger = logging.getLogger(__name__)

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        user_id: str = payload.get("sub")
        email: str = payload.get("email")
        role: str = payload.get("role")
        permissions: list = payload.get("permissions", [])

        if user_id is None:
            return None

        return TokenData(
            user_id=user_id,
            email=email,
            role=role,
            permissions=permissions,
        )
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None


def get_user_by_email(email: str) -> Optional[dict]:
    db = get_mongodb()
    user = db.users.find_one({"email": email})
    return user


def get_user_by_id(user_id: str) -> Optional[dict]:
    db = get_mongodb()
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        return user
    except Exception as e:
        logger.error(f"Error getting user by ID: {e}")
        return None


def get_role_permissions(role_name: str) -> list:
    db = get_mongodb()
    role = db.roles.find_one({"name": role_name})
    if role:
        return role.get("permissions", [])
    return []


def authenticate_user(email: str, password: str) -> Optional[dict]:
    user = get_user_by_email(email)
    if not user:
        logger.warning(f"Authentication failed: user not found for email {email}")
        return None
    if not verify_password(password, user["password"]):
        logger.warning(f"Authentication failed: invalid password for email {email}")
        return None
    if not user.get("is_active", True):
        logger.warning(f"Authentication failed: user inactive for email {email}")
        return None
    logger.info(f"User authenticated successfully: {email}")
    return user


def create_user(user_data: UserCreate) -> Optional[dict]:
    db = get_mongodb()

    existing = db.users.find_one({"$or": [
        {"email": user_data.email},
        {"username": user_data.username}
    ]})
    if existing:
        logger.warning("User creation failed: email or username already exists")
        return None

    role = db.roles.find_one({"name": user_data.role})
    if not role:
        logger.warning(f"User creation failed: role {user_data.role} not found")
        return None

    now = datetime.utcnow()
    user_doc = {
        "username": user_data.username,
        "email": user_data.email,
        "password": get_password_hash(user_data.password),
        "first_name": user_data.first_name,
        "last_name": user_data.last_name,
        "role": user_data.role,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
    }

    result = db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    logger.info(f"User created successfully: {user_data.email}")
    return user_doc


def has_permission(user_role: str, required_permission: str) -> bool:
    permissions = get_role_permissions(user_role)
    if "all" in permissions:
        return True
    return required_permission in permissions


def format_user_response(user: dict) -> dict:
    return {
        "_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "role": user["role"],
        "is_active": user.get("is_active", True),
        "created_at": user["created_at"],
        "updated_at": user["updated_at"],
    }
