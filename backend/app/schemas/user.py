from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserRead(BaseModel):
    id: UUID
    email: str
    name: str
    health_goals_json: dict | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserSettingsUpdate(BaseModel):
    health_goals_json: dict | None = None
    name: str | None = None
