from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

# Pydantic Models


# Only require fields that the frontend provides for registration
class UserCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=254)
    password: str = Field(..., min_length=1)


class UserUpdate(BaseModel):
    user_id: str | None = Field(None, min_length=1, max_length=100)
    first_name: str | None = Field(None, min_length=1, max_length=100)
    last_name: str | None = Field(None, min_length=1, max_length=100)
    display_name: str | None = Field(None, min_length=1, max_length=200)
    email: str | None = Field(None, min_length=1, max_length=254)
    is_active: bool | None = None
    modified_by: str | None = Field(None, min_length=1, max_length=100)


class UserResponse(BaseModel):
    id: int
    user_id: str
    first_name: str
    last_name: str
    display_name: str
    email: str
    is_active: bool
    created_by: str
    modified_by: str
    created: datetime
    modified: datetime
    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    items: list[UserResponse]
    item_count: int = 0
    page_count: int = 0
    prev_page: int | None = None
    next_page: int | None = None


class UserRegistrationResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    first_name: str
    user_id: str
