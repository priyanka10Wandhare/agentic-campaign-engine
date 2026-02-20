from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Tenant, User
from app.schemas.user import UserCreate


class UserService:
    @staticmethod
    def create_user(db: Session, payload: UserCreate) -> User:
        tenant = db.get(Tenant, payload.tenant_id)
        if tenant is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

        user = User(email=payload.email, tenant_id=payload.tenant_id, role=payload.role)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
