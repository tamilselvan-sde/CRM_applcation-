import logging
from typing import Callable, List

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user import TokenData
from app.services.auth_service import decode_access_token, get_role_permissions

logger = logging.getLogger(__name__)

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    token = credentials.credentials
    token_data = decode_access_token(token)

    if token_data is None:
        logger.warning("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def require_permission(permission: str) -> Callable:
    async def permission_checker(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        permissions = get_role_permissions(current_user.role)

        if "all" in permissions:
            return current_user

        if permission not in permissions:
            logger.warning(
                f"Permission denied: user {current_user.email} lacks {permission}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission} required",
            )

        return current_user

    return permission_checker


def require_any_permission(permissions: List[str]) -> Callable:
    async def permission_checker(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        user_permissions = get_role_permissions(current_user.role)

        if "all" in user_permissions:
            return current_user

        for perm in permissions:
            if perm in user_permissions:
                return current_user

        logger.warning(
            f"Permission denied: user {current_user.email} lacks any of {permissions}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission denied: one of {permissions} required",
        )

    return permission_checker


def require_role(roles: List[str]) -> Callable:
    async def role_checker(
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        if current_user.role not in roles:
            logger.warning(
                f"Role denied: user {current_user.email} has role {current_user.role}, "
                f"required one of {roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role denied: one of {roles} required",
            )

        return current_user

    return role_checker


class PermissionChecker:
    def __init__(self, required_permission: str):
        self.required_permission = required_permission

    async def __call__(
        self,
        current_user: TokenData = Depends(get_current_user),
    ) -> TokenData:
        permissions = get_role_permissions(current_user.role)

        if "all" in permissions:
            return current_user

        if self.required_permission not in permissions:
            logger.warning(
                f"Permission denied: user {current_user.email} lacks "
                f"{self.required_permission}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.required_permission} required",
            )

        return current_user
