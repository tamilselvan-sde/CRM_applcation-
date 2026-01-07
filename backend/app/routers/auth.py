import logging
from datetime import timedelta
from typing import List

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status

from app.config import get_settings
from app.database.mongodb import get_mongodb
from app.middleware.auth_middleware import get_current_user, require_role
from app.schemas.user import (
    RoleResponse,
    Token,
    TokenData,
    UserCreate,
    UserLogin,
    UserResponse,
    UserUpdate,
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_user,
    format_user_response,
    get_role_permissions,
    get_user_by_id,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate) -> UserResponse:
    logger.info(f"Registration attempt for email: {user_data.email}")

    user = create_user(user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already exists, or invalid role",
        )

    return UserResponse(**format_user_response(user))


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin) -> Token:
    logger.info(f"Login attempt for email: {credentials.email}")

    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    permissions = get_role_permissions(user["role"])

    access_token = create_access_token(
        data={
            "sub": str(user["_id"]),
            "email": user["email"],
            "role": user["role"],
            "permissions": permissions,
        },
        expires_delta=timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )

    logger.info(f"Login successful for email: {credentials.email}")
    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: TokenData = Depends(get_current_user),
) -> UserResponse:
    user = get_user_by_id(current_user.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(**format_user_response(user))


@router.get("/roles", response_model=List[RoleResponse])
async def get_roles(
    current_user: TokenData = Depends(get_current_user),
) -> List[RoleResponse]:
    db = get_mongodb()
    roles = list(db.roles.find())

    return [
        RoleResponse(
            _id=str(role["_id"]),
            name=role["name"],
            description=role.get("description"),
            permissions=role.get("permissions", []),
        )
        for role in roles
    ]


@router.get("/users", response_model=List[UserResponse])
async def get_users(
    current_user: TokenData = Depends(require_role(["admin"])),
) -> List[UserResponse]:
    db = get_mongodb()
    users = list(db.users.find())

    return [UserResponse(**format_user_response(user)) for user in users]


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: TokenData = Depends(require_role(["admin"])),
) -> UserResponse:
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return UserResponse(**format_user_response(user))


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: TokenData = Depends(require_role(["admin"])),
) -> UserResponse:
    db = get_mongodb()

    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    existing_user = db.users.find_one({"_id": obj_id})
    if not existing_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    update_data = user_update.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    if "role" in update_data:
        role = db.roles.find_one({"name": update_data["role"]})
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role {update_data['role']} not found",
            )

    from datetime import datetime
    update_data["updated_at"] = datetime.utcnow()

    db.users.update_one({"_id": obj_id}, {"$set": update_data})

    updated_user = db.users.find_one({"_id": obj_id})
    logger.info(f"User updated: {user_id}")

    return UserResponse(**format_user_response(updated_user))


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: TokenData = Depends(require_role(["admin"])),
) -> None:
    db = get_mongodb()

    try:
        obj_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user ID format",
        )

    if str(obj_id) == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account",
        )

    result = db.users.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    logger.info(f"User deleted: {user_id}")
