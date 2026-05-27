from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, Union
from urllib.parse import urlparse

VALID_EXPORT_FORMATS = {"json", "jsonl", "csv", "rdf"}
_EXTENSIONS = {
    "json": ".json",
    "jsonl": ".jsonl",
    "csv": ".csv",
    "rdf": ".ttl",
}


def save_payload(
    payload: Any,
    path: Union[str, Path],
    *,
    format: str = "json",
    overwrite: bool = False,
    default_stem: str = "umls_response",
) -> Path:
    """Save a UMLS payload or response object to disk."""
    output_format = _normalize_format(format)
    default_stem = _default_stem(payload, default_stem)
    target = _resolve_output_path(Path(path), output_format, default_stem)
    if target.exists() and not overwrite:
        raise FileExistsError("{0} already exists.".format(target))
    target.parent.mkdir(parents=True, exist_ok=True)

    if output_format == "json":
        target.write_text(
            json.dumps(_to_payload(payload), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    elif output_format == "jsonl":
        lines = [
            json.dumps(item, ensure_ascii=False, default=str)
            for item in records_from_payload(payload)
        ]
        target.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    elif output_format == "csv":
        _write_csv(target, records_from_payload(payload))
    else:
        from umls_python_client.formatting import to_rdf

        target.write_text(to_rdf(_to_payload(payload)), encoding="utf-8")

    return target


def records_from_payload(payload: Any) -> list[Any]:
    """Return the record list represented by a UMLS payload."""
    value = _to_payload(payload)
    if isinstance(value, Mapping):
        if isinstance(value.get("releaseTypes"), list):
            return list(value["releaseTypes"])
        result = value.get("result", value)
        if isinstance(result, Mapping) and isinstance(result.get("results"), list):
            return list(result["results"])
        if isinstance(result, list):
            return list(result)
        return [result]
    if isinstance(value, list):
        return value
    return [value]


def _write_csv(path: Path, records: Sequence[Any]) -> None:
    rows = [_flatten_record(record) for record in records]
    fieldnames = _fieldnames(rows)
    with path.open("w", newline="", encoding="utf-8") as handle:
        if not fieldnames:
            handle.write("")
            return
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _flatten_record(record: Any) -> dict[str, Any]:
    if not isinstance(record, Mapping):
        return {"value": record}
    flattened: dict[str, Any] = {}
    _flatten_mapping(record, flattened)
    return flattened


def _flatten_mapping(
    record: Mapping[str, Any],
    flattened: dict[str, Any],
    prefix: str = "",
) -> None:
    for key, value in record.items():
        name = "{0}.{1}".format(prefix, key) if prefix else str(key)
        if isinstance(value, Mapping):
            _flatten_mapping(value, flattened, name)
        elif isinstance(value, list):
            flattened[name] = _flatten_list(value)
        else:
            flattened[name] = value


def _flatten_list(value: list[Any]) -> str:
    if all(not isinstance(item, (Mapping, list)) for item in value):
        return "|".join("" if item is None else str(item) for item in value)
    return json.dumps(value, ensure_ascii=False, default=str)


def _fieldnames(rows: Iterable[Mapping[str, Any]]) -> list[str]:
    names: list[str] = []
    seen: set[str] = set()
    for row in rows:
        for name in row:
            if name not in seen:
                seen.add(name)
                names.append(name)
    return names


def _to_payload(payload: Any) -> Any:
    if hasattr(payload, "to_dict"):
        return payload.to_dict()
    return payload


def _resolve_output_path(path: Path, output_format: str, default_stem: str) -> Path:
    if path.exists() and path.is_dir():
        return path / "{0}{1}".format(
            _safe_stem(default_stem), _EXTENSIONS[output_format]
        )
    if path.suffix:
        return path
    return path / "{0}{1}".format(_safe_stem(default_stem), _EXTENSIONS[output_format])


def _normalize_format(output_format: str) -> str:
    normalized = output_format.lower()
    if normalized not in VALID_EXPORT_FORMATS:
        allowed = ", ".join(sorted(VALID_EXPORT_FORMATS))
        raise ValueError(
            "Invalid export format '{0}'. Allowed formats: {1}.".format(
                output_format,
                allowed,
            )
        )
    return normalized


def _safe_stem(value: str) -> str:
    stem = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in value
    ).strip("_")
    if len(stem) > 160:
        stem = stem[:160].rstrip("_")
    return stem or "umls_response"


def _default_stem(payload: Any, fallback: str) -> str:
    metadata = getattr(payload, "request_metadata", None)
    if isinstance(metadata, Mapping):
        stem = _stem_from_metadata(metadata)
        if stem:
            return stem
    return fallback


def _stem_from_metadata(metadata: Mapping[str, Any]) -> str:
    parts: list[str] = []
    source = metadata.get("path") or metadata.get("absolute_url")
    if isinstance(source, str):
        parsed = urlparse(source)
        source_path = parsed.path if parsed.scheme or parsed.netloc else source
        parts.extend(
            segment
            for segment in source_path.split("/")
            if segment and segment != "rest"
        )

    params = metadata.get("params")
    if isinstance(params, Mapping):
        preferred_keys = (
            "string",
            "ui",
            "id",
            "source",
            "targetSource",
            "releaseType",
        )
        keys = [key for key in preferred_keys if key in params] + [
            key for key in sorted(params) if key not in preferred_keys
        ]
        for key in keys:
            if key.lower() in {"apikey", "validatorapikey"}:
                continue
            value = params[key]
            if value is None or value == "":
                continue
            parts.append("{0}_{1}".format(key, value))

    return "_".join(str(part) for part in parts)
