import uuid

import structlog
from fastapi import FastAPI, Request


async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id", str(uuid.uuid4()))
    request.state.request_id = request_id

    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(request_id=request_id, path=request.url.path, method=request.method)

    response = await call_next(request)
    response.headers["x-request-id"] = request_id
    return response


def register_middlewares(app: FastAPI) -> None:
    app.middleware("http")(request_context_middleware)
