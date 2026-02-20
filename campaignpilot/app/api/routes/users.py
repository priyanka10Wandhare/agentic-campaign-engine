from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db_session
from app.schemas.user import UserCreate, UserRead
from app.services import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserRead, status_code=201)
def create_user(payload: UserCreate, db: Session = Depends(get_db_session)) -> UserRead:
    return UserService.create_user(db, payload)
