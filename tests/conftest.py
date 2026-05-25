from __future__ import annotations

import json
from typing import Any, Callable, List

import httpx
import pytest


def json_response(payload: Any, status_code: int = 200) -> httpx.Response:
    return httpx.Response(
        status_code=status_code,
        headers={"content-type": "application/json"},
        content=json.dumps(payload).encode("utf-8"),
    )


@pytest.fixture
def captured_requests() -> List[httpx.Request]:
    return []


@pytest.fixture
def mock_transport(
    captured_requests: List[httpx.Request],
) -> Callable[[Any], httpx.MockTransport]:
    def factory(payload: Any) -> httpx.MockTransport:
        def handler(request: httpx.Request) -> httpx.Response:
            captured_requests.append(request)
            return json_response(payload)

        return httpx.MockTransport(handler)

    return factory
