from fastapi import APIRouter

from app.errors.exceptions import ResourceNotFoundError

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/missing")
def missing_resource() -> None:
    raise ResourceNotFoundError("Example missing resource")
