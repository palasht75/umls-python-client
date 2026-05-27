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


@pytest.mark.asyncio
async def test_async_helpers_auth_release_and_bulk_search(tmp_path) -> None:
    seen: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        if request.url.host == "utslogin.nlm.nih.gov":
            return httpx.Response(200, text="true")
        if request.url.path == "/releases":
            return httpx.Response(
                200,
                json={
                    "releaseTypes": [
                        {
                            "product": "UMLS",
                            "releaseType": "UMLS Full Release",
                            "endpoint": "https://uts-ws.nlm.nih.gov/releases?releaseType=umls-full-release",
                        }
                    ]
                },
            )
        if request.url.path == "/download":
            return httpx.Response(200, content=b"archive")
        return httpx.Response(
            200,
            json={"result": {"results": [{"ui": "C1", "name": "Diabetes"}]}},
        )

    async with AsyncUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(handler),
    ) as client:
        validation = await client.auth_api.validate_user("user-key")
        releases = await client.release_api.list_releases(current=True)
        searches = await client.search_api.bulk_search(["diabetes", "asthma"])
        output = await client.release_api.download_file(
            "https://download.nlm.nih.gov/umls/kss/example.zip",
            tmp_path,
        )

    assert validation.result.valid is True
    assert releases.result[0].product == "UMLS"
    assert set(searches) == {"diabetes", "asthma"}
    assert output.read_bytes() == b"archive"
    assert seen[0].url.params["validatorApiKey"] == "secret"
