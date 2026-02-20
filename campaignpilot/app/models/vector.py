from sqlalchemy.types import UserDefinedType


class Vector(UserDefinedType):
    """Minimal pgvector column type for SQLAlchemy without external dependencies."""

    cache_ok = True

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    def get_col_spec(self, **kw: object) -> str:
        return f"vector({self.dimension})"
