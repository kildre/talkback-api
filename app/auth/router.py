from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.users.models import DBUser

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    first_name: str


# Dummy JWT generator for demo (replace with real JWT in production)
def create_jwt(user_id: str) -> str:
    return f"fake-jwt-token-for-{user_id}"


@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(DBUser).filter(DBUser.email == request.email).first()
    if not user or user.hashed_password != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_jwt(user.user_id)
    return LoginResponse(access_token=token, first_name=user.first_name)
