from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str
    db_name: str = "nigrani_setu"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120

    cors_origins: str = "http://localhost:5173"

    class Config:
        env_file = ".env"

    @property
    def cors_origin_list(self):
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
