from sqlalchemy.orm import Session

from app.models import Tenant
from app.schemas.tenant import TenantCreate


class TenantService:
    @staticmethod
    def create_tenant(db: Session, payload: TenantCreate) -> Tenant:
        tenant = Tenant(name=payload.name)
        db.add(tenant)
        db.commit()
        db.refresh(tenant)
        return tenant
