from typing import Annotated

from fastapi import APIRouter, Depends
from starlette import status

from app.auth import validate_jwt
from app.config import settings

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/admin",
    tags=["Admin"],
)


@router.get(
    "/current-user",
    status_code=status.HTTP_200_OK,
)
async def get_current_user(current_user: Annotated[dict, Depends(validate_jwt)]):
    return {"user": current_user}
