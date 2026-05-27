from __future__ import annotations

import httpx
import pytest

from umls_python_client import AsyncUMLSClient, SearchResult
from umls_python_client.errors import UMLSRequestError


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
            return httpx.Response(
                302,
                headers={"location": "https://uts-ws.nlm.nih.gov/final.zip"},
            )
        if request.url.path == "/final.zip":
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
    assert releases.result[0].current is None
    assert set(searches) == {"diabetes", "asthma"}
    assert output.read_bytes() == b"archive"
    assert seen[0].url.params["validatorApiKey"] == "secret"
    zip_paths = [
        request.url.path for request in seen if request.url.path.endswith(".zip")
    ]
    assert zip_paths == ["/final.zip"]


@pytest.mark.asyncio
async def test_async_follow_url_rejects_untrusted_hosts_before_request() -> None:
    seen: list[httpx.Request] = []

    async def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"result": []})

    async with AsyncUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(handler),
    ) as client:
        with pytest.raises(UMLSRequestError):
            await client.follow_url("https://example.com/not-umls")

    assert seen == []


@pytest.mark.asyncio
async def test_async_concept_profile_collects_all_documented_pages() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if path.endswith("/atoms/preferred"):
            return httpx.Response(
                200,
                json={"result": {"classType": "Atom", "ui": "A1", "name": "Diabetes"}},
            )
        if path.endswith("/definitions"):
            page = int(request.url.params["pageNumber"])
            return httpx.Response(
                200,
                json={
                    "pageNumber": page,
                    "pageCount": 2,
                    "result": [
                        {
                            "classType": "Definition",
                            "value": "Definition {0}".format(page),
                        }
                    ],
                },
            )
        if path.endswith("/relations"):
            page = int(request.url.params["pageNumber"])
            return httpx.Response(
                200,
                json={
                    "pageNumber": page,
                    "pageCount": 2,
                    "result": [
                        {"classType": "ConceptRelation", "ui": "R{0}".format(page)}
                    ],
                },
            )
        return httpx.Response(
            200,
            json={"result": {"classType": "Concept", "ui": "C0011849"}},
        )

    async with AsyncUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(handler),
    ) as client:
        profile = (await client.cui_api.get_concept_profile("C0011849")).result

    assert [definition.value for definition in profile.definitions] == [
        "Definition 1",
        "Definition 2",
    ]
    assert [relation.ui for relation in profile.relations] == ["R1", "R2"]
