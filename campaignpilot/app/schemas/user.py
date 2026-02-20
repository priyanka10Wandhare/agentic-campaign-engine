from pydantic import BaseModel, ConfigDict, EmailStr

from app.models import UserRole


class UserCreate(BaseModel):
    email: EmailStr
    tenant_id: int
    role: UserRole


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    tenant_id: int
    role: UserRole
