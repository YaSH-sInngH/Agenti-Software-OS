from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    PINECONE_API_KEY: str
    PINECONE_INDEX: str
    WORKSPACE_DIR: str
    ANTHROPIC_API_KEY: str
    MODEL_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
    
settings = Settings()