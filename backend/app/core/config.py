from functools import cached_property
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Knowledge Sharing and Innovation System"
    api_prefix: str = "/api"
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "ltygxz712"
    mysql_db: str = "bysj"
    secret_key: str = "knowledge-innovation-system-secret-key"
    access_token_expire_minutes: int = 1440
    init_admin_username: str = "admin"
    init_admin_password: str = "admin123456"

    @cached_property
    def database_url(self) -> str:
        encoded_user = quote_plus(self.mysql_user)
        encoded_password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{encoded_user}:{encoded_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )


settings = Settings()
