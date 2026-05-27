from __future__ import annotations

import httpx
import pytest

from umls_python_client.errors import UMLSDecodeError, UMLSHTTPError, UMLSRequestError
from umls_python_client.transport import SyncUMLSTransport


def test_transport_injects_api_key_and_params() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"result": []})

    transport = SyncUMLSTransport(
        api_key="secret",
        transport=httpx.MockTransport(handler),
    )

    payload = transport.request("/search/current", params={"string": "diabetes"})

    assert payload == {"result": []}
    assert seen[0].url.params["apiKey"] == "secret"
    assert seen[0].url.params["string"] == "diabetes"


def test_transport_allows_authenticated_umls_absolute_urls() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"result": {"ui": "C1"}})

    transport = SyncUMLSTransport(
        api_key="secret",
        transport=httpx.MockTransport(handler),
    )

    transport.request(
        absolute_url="https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C1"
    )

    assert seen[0].url.params["apiKey"] == "secret"


def test_transport_rejects_authenticated_untrusted_absolute_urls() -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"result": []})

    transport = SyncUMLSTransport(
        api_key="secret",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(UMLSRequestError):
        transport.request(absolute_url="https://example.com/steal")

    assert seen == []


def test_transport_retries_retryable_status() -> None:
    calls = 0

    def handler(_request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(503, text="try again")
        return httpx.Response(200, json={"result": {"name": "ok"}})

    transport = SyncUMLSTransport(
        api_key="secret",
        retries=1,
        transport=httpx.MockTransport(handler),
    )

    assert transport.request("/content/current/CUI/C0000000")["result"]["name"] == "ok"
    assert calls == 2


def test_transport_raises_for_http_errors() -> None:
    transport = SyncUMLSTransport(
        api_key="secret",
        retries=0,
        transport=httpx.MockTransport(lambda _request: httpx.Response(401, text="no")),
    )

    with pytest.raises(UMLSHTTPError) as exc_info:
        transport.request("/content/current/CUI/C0000000")

    assert exc_info.value.status_code == 401
    assert "Invalid API Key" in exc_info.value.to_dict()["error"]


def test_transport_raises_for_non_json_response() -> None:
    transport = SyncUMLSTransport(
        api_key="secret",
        transport=httpx.MockTransport(lambda _request: httpx.Response(200, text="no")),
    )

    with pytest.raises(UMLSDecodeError):
        transport.request("/content/current/CUI/C0000000")


def test_transport_raises_for_network_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("network down", request=request)

    transport = SyncUMLSTransport(
        api_key="secret",
        retries=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(UMLSRequestError) as exc_info:
        transport.request("/content/current/CUI/C0000000")

    assert "network down" in str(exc_info.value)
