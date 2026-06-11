from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.db.database import get_db

from src.core.schemas.auth import SignupRequest, LoginRequest

from src.auth.user_service import (
    get_user_by_email,
    create_user,
)

from src.auth.security import (
    hash_password,
    verify_password,
)

from src.auth.jwt import create_access_token

from src.auth.dependencies import get_current_user

from src.workspaces.service import WorkspaceService

from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)

@router.post("/signup")
def signup(
    payload: SignupRequest,
    db: Session = Depends(get_db),
):

    existing_user = get_user_by_email(
        db,
        payload.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists",
        )

    user = create_user(
        db=db,
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(
            payload.password
        ),
    )

    # Every user starts with a default workspace.
    WorkspaceService.create(
        db,
        user.id,
        "Default Workspace",
    )

    return ok(
        {
            "message": "User created successfully",
            "user_id": user.id,
        }
    )

@router.post("/login")
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):

    user = get_user_by_email(
        db,
        payload.email,
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    valid = verify_password(
        payload.password,
        user.password_hash,
    )

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    token = create_access_token(
        {
            "user_id": user.id,
            "email": user.email,
        }
    )

    return ok(
        {
            "access_token": token,
            "token_type": "bearer",
        }
    )

@router.get("/me")
def me(
    current_user=Depends(get_current_user),
):

    return ok(
        {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        }
    )