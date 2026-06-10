from fastapi import FastAPI
from src.core.config.settings import settings
from src.core.db.database import Base
from src.core.db.database import engine
from src.core.db import models
from src.api.auth.routes import router as auth_router
from src.api.chat.routes import router as chat_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
)

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
    }

app.include_router(auth_router)
app.include_router(chat_router)