from __future__ import annotations

import csv
import json

import httpx
import pytest

from umls_python_client import UMLSClient, UMLSResponse


def test_response_save_jsonl_csv_and_rdf(tmp_path) -> None:
    response = UMLSResponse.from_payload(
        {
            "result": [
                {"classType": "Concept", "ui": "C1", "name": "First"},
                {"classType": "Concept", "ui": "C2", "name": "Second"},
            ]
        }
    )

    jsonl_path = response.save(tmp_path / "records", format="jsonl")
    csv_path = response.save(tmp_path / "records.csv", format="csv")
    rdf_path = response.save(tmp_path / "records.ttl", format="rdf")

    assert jsonl_path == tmp_path / "records" / "umls_response.jsonl"
    assert json.loads(jsonl_path.read_text().splitlines()[0])["ui"] == "C1"

    with csv_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[1]["name"] == "Second"
    assert "First" in rdf_path.read_text()


def test_export_overwrite_is_explicit(tmp_path) -> None:
    response = UMLSResponse.from_payload({"result": {"ui": "C1"}})
    target = response.save(tmp_path / "payload.json", format="json")

    with pytest.raises(FileExistsError):
        response.save(target, format="json")

    response.save(target, format="json", overwrite=True)
    assert json.loads(target.read_text())["result"]["ui"] == "C1"


def test_client_export_handles_existing_directory_with_suffix(tmp_path) -> None:
    response = UMLSResponse.from_payload(
        {"releaseTypes": [{"product": "UMLS", "releaseType": "UMLS Full Release"}]}
    )
    directory = tmp_path / "exports.v1"
    directory.mkdir()

    with UMLSClient(
        api_key="secret",
        http_transport=httpx.MockTransport(lambda _request: httpx.Response(200)),
    ) as client:
        output = client.export(response, directory, format="jsonl")

    assert output == directory / "umls_response.jsonl"
    assert json.loads(output.read_text())["product"] == "UMLS"
