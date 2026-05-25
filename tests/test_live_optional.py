from __future__ import annotations

import os

import pytest

from umls_python_client import TypedUMLSClient


@pytest.mark.live
def test_live_search_requires_explicit_api_key() -> None:
    api_key = os.getenv("UMLS_API_KEY")
    if not api_key:
        pytest.skip("UMLS_API_KEY is not set")

    with TypedUMLSClient(api_key=api_key) as client:
        response = client.search_api.search("diabetes", page_size=1)

    assert response.raw
