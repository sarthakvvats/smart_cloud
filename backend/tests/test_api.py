import asyncio

from app.main import health, generate_mock
from app.models import MockGenerateRequest


def test_health_and_generate_mock():
    h = asyncio.run(health())
    assert isinstance(h, dict)
    assert h.get("status") == "ok"

    req = MockGenerateRequest(n=5, seed=1)
    data = asyncio.run(generate_mock(req))
    assert isinstance(data, list)
    assert len(data) == 5
