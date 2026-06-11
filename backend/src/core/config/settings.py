from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    WORKSPACE_DIR: str
    WORKSPACES_ROOT: str = "workspaces"
    ANTHROPIC_API_KEY: str
    MODEL_NAME: str
    COHERE_API_KEY: str
    PINECONE_API_KEY: str
    PINECONE_INDEX_NAME: str
    CORS_ORIGINS: str = "http://localhost:3000,http://127.0.0.1:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.CORS_ORIGINS.split(",")
            if origin.strip()
        ]

settings = Settings()