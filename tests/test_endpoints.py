from __future__ import annotations

import httpx

from umls_python_client import UMLSClient


def test_search_endpoint_supports_current_filters_without_page_number(
    captured_requests: list[httpx.Request],
    mock_transport,
) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": {"results": []}}),
    )

    client.search_api.search(
        search_string="diabetes",
        page_number=9,
        page_size=10,
        semantic_types="T047",
        semantic_groups="Disorders",
        return_indented=False,
    )

    params = captured_requests[0].url.params
    assert captured_requests[0].url.path == "/rest/search/current"
    assert params["semanticTypes"] == "T047"
    assert params["semanticGroups"] == "Disorders"
    assert params["pageSize"] == "10"
    assert "pageNumber" not in params


def test_metadata_sources_does_not_send_api_key(
    captured_requests: list[httpx.Request],
    mock_transport,
) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": []}),
    )

    client.metadata_api.get_sources(return_indented=False)

    assert captured_requests[0].url.path == "/rest/metadata/current/sources"
    assert "apiKey" not in captured_requests[0].url.params


def test_cui_source_atom_crosswalk_and_semantic_paths(
    captured_requests: list[httpx.Request],
    mock_transport,
) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": []}),
    )

    client.cui_api.get_preferred_atom("C0011849", return_indented=False)
    client.source_api.get_source_preferred_atom(
        "SNOMEDCT_US", "73211009", return_indented=False
    )
    client.atom_api.get_ancestors("A123", return_indented=False)
    client.crosswalk_api.get_crosswalk("HPO", "HP:0001947", return_indented=False)
    client.semantic_network_api.get_semantic_type("T047", return_indented=False)

    paths = [request.url.path for request in captured_requests]
    assert paths == [
        "/rest/content/current/CUI/C0011849/atoms/preferred",
        "/rest/content/current/source/SNOMEDCT_US/73211009/atoms/preferred",
        "/rest/content/current/AUI/A123/ancestors",
        "/rest/crosswalk/current/source/HPO/HP:0001947",
        "/rest/semantic-network/current/TUI/T047",
    ]
