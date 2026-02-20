from pydantic import BaseModel, ConfigDict


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tenant_id: int
    entity_type: str
    entity_id: int
    action: str
    previous_state: dict | None
    new_state: dict | None
