from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from rdflib import Graph, Literal, Namespace, URIRef

VALID_OUTPUT_FORMATS = {"json", "rdf"}


def render_payload(
    payload: Any,
    output_format: str = "json",
    return_indented: bool = True,
) -> Any:
    """Render a payload using legacy JSON/RDF behavior."""
    if output_format not in VALID_OUTPUT_FORMATS:
        allowed = ", ".join(sorted(VALID_OUTPUT_FORMATS))
        raise ValueError(
            "Invalid format '{0}'. Allowed formats: {1}.".format(output_format, allowed)
        )

    if output_format == "rdf":
        return to_rdf(payload)

    if return_indented:
        if isinstance(payload, str):
            return payload
        return json.dumps(payload, indent=4)
    return payload


def save_output_to_file(response: Any, file_path: str) -> None:
    """Save response data to a file, creating parent directories as needed."""
    from umls_python_client.exports import save_payload

    if isinstance(response, str):
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(response, encoding="utf-8")
        return
    save_payload(response, file_path, format="json", overwrite=True)


def to_rdf(
    payload: Any,
    namespace_url: str = "https://uts-ws.nlm.nih.gov/rest/content/#",
) -> str:
    """Convert a UMLS JSON payload into simple Turtle RDF."""
    graph = Graph()
    umls = Namespace(namespace_url)
    for item in _iter_records(payload):
        if isinstance(item, Mapping):
            _add_record(graph, umls, item)
    return graph.serialize(format="turtle")


def _iter_records(payload: Any) -> Iterable[Any]:
    if hasattr(payload, "to_dict"):
        payload = payload.to_dict()
    if isinstance(payload, str):
        payload = json.loads(payload)
    if isinstance(payload, Mapping):
        result = payload.get("result", payload)
        if isinstance(result, Mapping) and isinstance(result.get("results"), list):
            return result["results"]
        if isinstance(result, list):
            return result
        return [result]
    if isinstance(payload, list):
        return payload
    return []


def _add_record(
    graph: Graph,
    namespace: Namespace,
    data: Mapping[str, Any],
) -> None:
    subject = _subject_for(namespace, data)
    for key, value in data.items():
        if value in (None, "NONE", ""):
            continue
        graph.add((subject, namespace[_safe_predicate(key)], _object_for(value)))


def _subject_for(namespace: Namespace, data: Mapping[str, Any]) -> URIRef:
    for key in ("uri", "id", "ui"):
        value = data.get(key)
        if isinstance(value, str) and value.startswith("http"):
            return URIRef(value)
        if isinstance(value, str) and value:
            return URIRef(str(namespace[value]))
    name = data.get("name", "unknown")
    return URIRef(str(namespace[str(name).replace(" ", "_")]))


def _object_for(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("http"):
        return URIRef(value)
    if isinstance(value, (dict, list)):
        return Literal(json.dumps(value, sort_keys=True))
    return Literal(value)


def _safe_predicate(name: str) -> str:
    return "".join(char if char.isalnum() or char == "_" else "_" for char in name)
