from __future__ import annotations

import httpx

from umls_python_client import (
    Concept,
    ReleaseInfo,
    TypedUMLSClient,
    UMLSResponse,
    UnknownRecord,
)
from umls_python_client.models import model_for_class_type


def test_typed_client_returns_models(mock_transport) -> None:
    client = TypedUMLSClient(
        api_key="secret",
        http_transport=mock_transport(
            {
                "result": {
                    "classType": "Concept",
                    "ui": "C0011849",
                    "name": "Diabetes Mellitus",
                }
            }
        ),
    )

    response = client.cui_api.get_cui_info("C0011849")

    assert isinstance(response, UMLSResponse)
    assert isinstance(response.result, Concept)
    assert response.result.name == "Diabetes Mellitus"
    assert response.to_dict()["result"]["ui"] == "C0011849"


def test_unknown_model_preserves_unknown_fields() -> None:
    record_type = model_for_class_type(
        {"classType": "UndocumentedThing", "customField": "value"}
    )
    record = record_type.from_dict(
        {"classType": "UndocumentedThing", "customField": "value"}
    )

    assert isinstance(record, UnknownRecord)
    assert record.to_dict()["customField"] == "value"


def test_release_info_current_preserves_unknown_state() -> None:
    assert ReleaseInfo.from_dict({"releaseType": "UMLS"}).current is None
    assert ReleaseInfo.from_dict({"current": True}).current is True
    assert ReleaseInfo.from_dict({"current": "false"}).current is False


def test_typed_client_raises_structured_errors() -> None:
    client = TypedUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(
            lambda _request: httpx.Response(500, text="server error")
        ),
        retries=0,
    )

    try:
        client.cui_api.get_cui_info("C0011849")
    except Exception as exc:  # noqa: BLE001
        assert exc.__class__.__name__ == "UMLSHTTPError"
    else:
        raise AssertionError("Expected UMLSHTTPError")
