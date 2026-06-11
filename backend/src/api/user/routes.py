from fastapi import APIRouter, Depends

from src.auth.dependencies import get_current_user
from src.core.utils.responses import ok

router = APIRouter(
    prefix="/api",
    tags=["User"],
)


@router.get("/me")
def get_me(
    current_user=Depends(get_current_user),
):
    return ok(
        {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
        }
    )
