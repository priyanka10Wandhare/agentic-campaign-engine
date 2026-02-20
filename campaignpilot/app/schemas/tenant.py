from pydantic import BaseModel, ConfigDict


class TenantCreate(BaseModel):
    name: str


class TenantRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
