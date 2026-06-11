from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.core.config.settings import settings
from src.core.db.database import Base
from src.core.db.database import engine
from src.core.db import models
from src.core.utils.responses import (
    http_exception_handler,
    validation_exception_handler,
    unhandled_exception_handler,
)
from src.api.auth.routes import router as auth_router
from src.api.chat.routes import router as chat_router
from src.api.user.routes import router as user_router
from src.api.workspaces.routes import router as workspaces_router
from src.api.orchestration.routes import router as orchestration_router
from src.api.agents.routes import router as agents_router
from src.api.tasks.routes import router as tasks_router
from src.api.reminders.routes import router as reminders_router
from src.api.knowledge.routes import router as knowledge_router
from src.api.dashboard.routes import router as dashboard_router
from src.api.runs.routes import router as runs_router
from src.api.memories.routes import router as memories_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(
    StarletteHTTPException,
    http_exception_handler,
)
app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler,
)
app.add_exception_handler(
    Exception,
    unhandled_exception_handler,
)

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
    }

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(user_router)
app.include_router(workspaces_router)
app.include_router(orchestration_router)
app.include_router(agents_router)
app.include_router(tasks_router)
app.include_router(reminders_router)
app.include_router(knowledge_router)
app.include_router(dashboard_router)
app.include_router(runs_router)
app.include_router(memories_router)
