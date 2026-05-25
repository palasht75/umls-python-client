from __future__ import annotations

import httpx
import pytest

from umls_python_client import AsyncUMLSClient, SearchResult


@pytest.mark.asyncio
async def test_async_client_returns_typed_response() -> None:
    seen: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(
            200,
            json={
                "result": {
                    "results": [
                        {"ui": "C0011849", "name": "Diabetes Mellitus"},
                    ]
                }
            },
        )

    async with AsyncUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(handler),
    ) as client:
        response = await client.search_api.search("diabetes", page_size=5)

    assert seen[0].url.path == "/rest/search/current"
    assert seen[0].url.params["apiKey"] == "secret"
    assert isinstance(response.result, list)
    assert isinstance(response.result[0], SearchResult)
    assert response.result[0].name == "Diabetes Mellitus"
