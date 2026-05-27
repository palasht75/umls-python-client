from __future__ import annotations

from contextlib import ExitStack

import httpx

from umls_python_client import ConceptProfile, TypedUMLSClient, UMLSClient


def test_auth_validation_constructs_uts_login_request(
    captured_requests: list[httpx.Request],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        return httpx.Response(200, text="true")

    client = UMLSClient(
        api_key="validator",
        http_transport=httpx.MockTransport(handler),
    )

    payload = client.auth_api.validate_user("user-key", return_indented=False)

    assert payload["valid"] is True
    assert captured_requests[0].url.host == "utslogin.nlm.nih.gov"
    assert captured_requests[0].url.params["validatorApiKey"] == "validator"
    assert captured_requests[0].url.params["apiKey"] == "user-key"


def test_release_list_and_download_requests(
    tmp_path,
    captured_requests: list[httpx.Request],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        if request.url.path == "/download":
            return httpx.Response(200, content=b"archive")
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

    with ExitStack() as stack:
        client = stack.enter_context(
            UMLSClient(
                api_key="secret",
                http_transport=httpx.MockTransport(handler),
            )
        )
        typed_client = stack.enter_context(
            TypedUMLSClient(
                api_key="secret",
                http_transport=httpx.MockTransport(handler),
            )
        )
        releases = client.release_api.list_releases(current=True, return_indented=False)
        typed_releases = typed_client.release_api.list_releases(current=True)
        output = client.release_api.download_file(
            "https://download.nlm.nih.gov/umls/kss/example.zip",
            tmp_path,
        )

    assert releases["releaseTypes"][0]["product"] == "UMLS"
    assert typed_releases.result[0].product == "UMLS"
    assert typed_releases.result[0].url.endswith("umls-full-release")
    assert "apiKey" not in captured_requests[0].url.params
    assert "apiKey" not in captured_requests[1].url.params
    assert captured_requests[2].url.params["apiKey"] == "secret"
    assert captured_requests[2].url.params["url"].endswith("example.zip")
    assert output.read_bytes() == b"archive"


def test_typed_concept_profile_and_follow_url(
    captured_requests: list[httpx.Request],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        path = request.url.path
        if path.endswith("/atoms/preferred"):
            return httpx.Response(
                200,
                json={"result": {"classType": "Atom", "ui": "A1", "name": "Diabetes"}},
            )
        if path.endswith("/definitions"):
            return httpx.Response(
                200,
                json={
                    "pageNumber": 1,
                    "pageCount": 1,
                    "result": [{"classType": "Definition", "value": "Definition"}],
                },
            )
        if path.endswith("/relations"):
            return httpx.Response(
                200,
                json={
                    "pageNumber": 1,
                    "pageCount": 1,
                    "result": [{"classType": "ConceptRelation", "ui": "R1"}],
                },
            )
        return httpx.Response(
            200,
            json={
                "result": {
                    "classType": "Concept",
                    "ui": "C0011849",
                    "name": "Diabetes",
                    "atoms": "https://uts-ws.nlm.nih.gov/rest/content/current/CUI/C0011849/atoms",
                }
            },
        )

    client = TypedUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(handler),
    )

    profile = client.cui_api.get_concept_profile("C0011849").result
    followed = client.follow_url(profile.concept.raw["atoms"])

    assert isinstance(profile, ConceptProfile)
    assert profile.concept.name == "Diabetes"
    assert profile.definitions[0].value == "Definition"
    assert followed.raw["result"]["ui"] == "C0011849"
    assert captured_requests[-1].url.params["apiKey"] == "secret"


def test_bulk_helpers_metadata_lookup_and_paginated_iterator(
    captured_requests: list[httpx.Request],
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        captured_requests.append(request)
        path = request.url.path
        if path.endswith("/sources"):
            return httpx.Response(
                200,
                json={
                    "result": [
                        {
                            "classType": "RootSource",
                            "abbreviation": "SNOMEDCT_US",
                            "preferredName": "SNOMED CT US Edition",
                        }
                    ]
                },
            )
        if path.endswith("/relations"):
            page = int(request.url.params["pageNumber"])
            return httpx.Response(
                200,
                json={
                    "pageNumber": page,
                    "pageCount": 2,
                    "result": [{"classType": "ConceptRelation", "ui": f"R{page}"}],
                },
            )
        return httpx.Response(
            200,
            json={"result": {"results": [{"ui": "C1", "name": "Diabetes"}]}},
        )

    client = TypedUMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(handler),
    )

    searches = client.search_api.bulk_search(["diabetes", "asthma"])
    sources = client.metadata_api.find_source(abbreviation="SNOMEDCT_US")
    relations = list(client.cui_api.iter_relations("C0011849"))

    assert set(searches) == {"diabetes", "asthma"}
    assert sources.result[0].abbreviation == "SNOMEDCT_US"
    assert [relation.ui for relation in relations] == ["R1", "R2"]


def test_source_hierarchy_keeps_documented_pagination(
    captured_requests: list[httpx.Request],
    mock_transport,
) -> None:
    client = UMLSClient(
        api_key="secret",
        http_transport=mock_transport({"result": []}),
    )

    client.source_api.get_source_parents(
        "SNOMEDCT_US",
        "9468002",
        page_number=3,
        page_size=10,
        return_indented=False,
    )
    client.atom_api.get_parents("A123", page_size=10, return_indented=False)

    assert captured_requests[0].url.params["pageNumber"] == "3"
    assert "pageNumber" not in captured_requests[1].url.params
