from __future__ import annotations

import json

import httpx

from umls_python_client import UMLSClient
from umls_python_client.searchAPI.search_api import SearchAPI


def test_existing_import_paths_and_aliases_work(mock_transport) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": {"results": []}}),
    )

    assert SearchAPI is not None
    assert client.search_api is client.searchAPI
    assert client.source_api is client.sourceAPI
    assert client.cui_api is client.cuiAPI
    assert client.semantic_network_api is client.semanticNetworkAPI
    assert client.crosswalk_api is client.crosswalkAPI
    assert client.metadata_api is client.metadataAPI
    assert client.atom_api is client.atomAPI
    assert client.auth_api is client.authAPI
    assert client.release_api is client.releaseAPI


def test_legacy_json_string_default_and_raw_mode(mock_transport) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": {"name": "Diabetes"}}),
    )

    pretty = client.cui_api.get_cui_info("C0011849")
    raw = client.cui_api.get_cui_info("C0011849", return_indented=False)

    assert isinstance(pretty, str)
    assert json.loads(pretty)["result"]["name"] == "Diabetes"
    assert raw == {"result": {"name": "Diabetes"}}


def test_legacy_rdf_mode(mock_transport) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport(
            {"result": {"classType": "Concept", "ui": "C0011849", "name": "Diabetes"}}
        ),
    )

    rdf = client.cui_api.get_cui_info("C0011849", format="rdf")

    assert "Diabetes" in rdf


def test_legacy_file_output_creates_parent_directory(tmp_path, mock_transport) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": {"name": "Diabetes"}}),
    )

    client.cui_api.get_cui_info(
        "C0011849",
        save_to_file=True,
        file_path=str(tmp_path / "nested"),
    )

    output_file = tmp_path / "nested" / "cui_info_C0011849.txt"
    assert output_file.exists()
    assert json.loads(output_file.read_text())["result"]["name"] == "Diabetes"


def test_legacy_http_error_returns_payload_not_exception() -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(
            lambda _request: httpx.Response(404, text="missing")
        ),
    )

    payload = client.cui_api.get_cui_info("C0000000", return_indented=False)

    assert payload["status_code"] == 404
    assert payload["error"] == "Resource not found."
