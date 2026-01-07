import logging
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "CRM Application"
    debug: bool = False

    postgres_host: str = "postgres"
    postgres_port: int = 5432
    postgres_user: str = "crm_user"
    postgres_password: str = "crm_password"
    postgres_db: str = "crm_data"

    mongodb_host: str = "mongodb"
    mongodb_port: int = 27017
    mongodb_user: str = "crm_user"
    mongodb_password: str = "crm_password"
    mongodb_db: str = "crm_auth"

    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def mongodb_url(self) -> str:
        return (
            f"mongodb://{self.mongodb_user}:{self.mongodb_password}"
            f"@{self.mongodb_host}:{self.mongodb_port}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )
