from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.tenant import TenantCreate, TenantRead
from app.services import TenantService

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantRead, status_code=201)
def create_tenant(payload: TenantCreate, db: Session = Depends(get_db_session)) -> TenantRead:
    return TenantService.create_tenant(db, payload)
