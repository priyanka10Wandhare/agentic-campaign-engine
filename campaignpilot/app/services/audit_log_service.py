from sqlalchemy.orm import Session

from app.models import AuditLog


class AuditLogService:
    @staticmethod
    def create_log(
        db: Session,
        *,
        tenant_id: int,
        entity_type: str,
        entity_id: int,
        action: str,
        previous_state: dict | None,
        new_state: dict | None,
    ) -> AuditLog:
        log = AuditLog(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            previous_state=previous_state,
            new_state=new_state,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log
