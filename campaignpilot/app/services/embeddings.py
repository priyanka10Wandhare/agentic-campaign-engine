import hashlib
import json
from urllib import request

from app.core.config import get_settings

EMBEDDING_DIMENSION = 1536


def generate_embedding(text_value: str) -> list[float]:
    """Generate embeddings from OpenAI when configured, otherwise deterministic mock vectors."""

    settings = get_settings()
    if settings.openai_api_key:
        return _openai_embedding(text_value, settings.openai_api_key, settings.openai_embedding_model)

    return _mock_embedding(text_value)


def _mock_embedding(text_value: str) -> list[float]:
    digest = hashlib.sha256(text_value.encode("utf-8")).digest()
    values: list[float] = []
    for index in range(EMBEDDING_DIMENSION):
        byte_value = digest[index % len(digest)]
        values.append((byte_value / 255.0) * 2 - 1)

    return values


def _openai_embedding(text_value: str, api_key: str, model: str) -> list[float]:
    payload = json.dumps({"input": text_value, "model": model}).encode("utf-8")
    req = request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        body = json.loads(response.read().decode("utf-8"))

    return body["data"][0]["embedding"]
