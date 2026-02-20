from collections.abc import Awaitable, Callable

from fastapi import Request
from starlette.responses import Response


async def tenant_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    tenant_header = request.headers.get("X-Tenant-ID")
    request.state.tenant_id = int(tenant_header) if tenant_header and tenant_header.isdigit() else None
    return await call_next(request)
