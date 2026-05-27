from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Generic, List, Mapping, Optional, TypeVar, Union

T = TypeVar("T")


def _as_dict(data: Mapping[str, Any]) -> Dict[str, Any]:
    return dict(data)


def _get(data: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in data:
            return data[name]
    return None


def _to_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "valid", "1", "yes"}
    return bool(value)


def _to_optional_bool(value: Any) -> Optional[bool]:
    if value is None:
        return None
    return _to_bool(value)


@dataclass
class Record:
    """Base record with unknown-field preservation."""

    raw: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Record":
        return cls(raw=_as_dict(data))

    @property
    def class_type(self) -> Optional[str]:
        value = self.raw.get("classType")
        return value if isinstance(value, str) else None

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.raw)


@dataclass
class UnknownRecord(Record):
    """Fallback for UMLS records without a dedicated model."""

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "UnknownRecord":
        return cls(raw=_as_dict(data))


@dataclass
class SearchResult(Record):
    ui: Optional[str] = None
    name: Optional[str] = None
    root_source: Optional[str] = None
    uri: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SearchResult":
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui"),
            name=_get(data, "name"),
            root_source=_get(data, "rootSource"),
            uri=_get(data, "uri"),
        )


@dataclass
class Concept(Record):
    ui: Optional[str] = None
    name: Optional[str] = None
    semantic_types: List[Dict[str, Any]] = field(default_factory=list)
    atom_count: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Concept":
        semantic_types = _get(data, "semanticTypes") or []
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui"),
            name=_get(data, "name"),
            semantic_types=list(semantic_types)
            if isinstance(semantic_types, list)
            else [],
            atom_count=_get(data, "atomCount"),
        )


@dataclass
class Atom(Record):
    ui: Optional[str] = None
    name: Optional[str] = None
    root_source: Optional[str] = None
    term_type: Optional[str] = None
    language: Optional[str] = None
    code: Optional[str] = None
    concept: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Atom":
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui"),
            name=_get(data, "name"),
            root_source=_get(data, "rootSource"),
            term_type=_get(data, "termType"),
            language=_get(data, "language"),
            code=_get(data, "code"),
            concept=_get(data, "concept"),
        )


@dataclass
class SourceAtomCluster(Record):
    ui: Optional[str] = None
    name: Optional[str] = None
    root_source: Optional[str] = None
    atom_count: Optional[int] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SourceAtomCluster":
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui"),
            name=_get(data, "name"),
            root_source=_get(data, "rootSource"),
            atom_count=_get(data, "atomCount"),
        )


@dataclass
class Definition(Record):
    value: Optional[str] = None
    root_source: Optional[str] = None
    source_originated: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Definition":
        return cls(
            raw=_as_dict(data),
            value=_get(data, "value"),
            root_source=_get(data, "rootSource"),
            source_originated=_get(data, "sourceOriginated"),
        )


@dataclass
class Relation(Record):
    ui: Optional[str] = None
    root_source: Optional[str] = None
    relation_label: Optional[str] = None
    additional_relation_label: Optional[str] = None
    related_id: Optional[str] = None
    related_id_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Relation":
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui"),
            root_source=_get(data, "rootSource"),
            relation_label=_get(data, "relationLabel"),
            additional_relation_label=_get(data, "additionalRelationLabel"),
            related_id=_get(data, "relatedId"),
            related_id_name=_get(data, "relatedIdName"),
        )


@dataclass
class Attribute(Record):
    ui: Optional[str] = None
    source_ui: Optional[str] = None
    root_source: Optional[str] = None
    name: Optional[str] = None
    value: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "Attribute":
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui"),
            source_ui=_get(data, "sourceUi"),
            root_source=_get(data, "rootSource"),
            name=_get(data, "name"),
            value=_get(data, "value"),
        )


@dataclass
class SemanticType(Record):
    ui: Optional[str] = None
    name: Optional[str] = None
    tree_number: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "SemanticType":
        return cls(
            raw=_as_dict(data),
            ui=_get(data, "ui", "tui"),
            name=_get(data, "name"),
            tree_number=_get(data, "treeNumber"),
        )


@dataclass
class RootSource(Record):
    abbreviation: Optional[str] = None
    expanded_form: Optional[str] = None
    family: Optional[str] = None
    language: Any = None
    restriction_level: Optional[int] = None
    short_name: Optional[str] = None
    preferred_name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "RootSource":
        return cls(
            raw=_as_dict(data),
            abbreviation=_get(data, "abbreviation"),
            expanded_form=_get(data, "expandedForm"),
            family=_get(data, "family"),
            language=_get(data, "language"),
            restriction_level=_get(data, "restrictionLevel"),
            short_name=_get(data, "shortName"),
            preferred_name=_get(data, "preferredName"),
        )


@dataclass
class LicenseValidation(Record):
    valid: bool = False
    status_code: Optional[int] = None
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "LicenseValidation":
        valid = _get(data, "valid", "isValid")
        return cls(
            raw=_as_dict(data),
            valid=_to_bool(valid),
            status_code=_get(data, "statusCode", "status_code"),
            message=_get(data, "message", "detail"),
        )


@dataclass
class ReleaseFile(Record):
    name: Optional[str] = None
    release_type: Optional[str] = None
    url: Optional[str] = None
    published_date: Optional[str] = None
    product: Optional[str] = None
    release_version: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReleaseFile":
        return cls(
            raw=_as_dict(data),
            name=_get(data, "name", "fileName", "filename"),
            release_type=_get(data, "releaseType", "type"),
            url=_get(data, "url", "downloadUrl", "downloadURL"),
            published_date=_get(data, "publishedDate", "releaseDate", "date"),
            product=_get(data, "product"),
            release_version=_get(data, "releaseVersion", "version"),
        )


@dataclass
class ReleaseInfo(Record):
    name: Optional[str] = None
    release_type: Optional[str] = None
    current: Optional[bool] = None
    url: Optional[str] = None
    product: Optional[str] = None
    endpoint: Optional[str] = None
    file_name: Optional[str] = None
    release_version: Optional[str] = None
    release_date: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReleaseInfo":
        return cls(
            raw=_as_dict(data),
            name=_get(data, "name", "releaseName", "fileName", "releaseType"),
            release_type=_get(data, "releaseType", "type"),
            current=_to_optional_bool(_get(data, "current", "isCurrent")),
            url=_get(data, "url", "downloadUrl", "downloadURL", "endpoint"),
            product=_get(data, "product"),
            endpoint=_get(data, "endpoint"),
            file_name=_get(data, "fileName", "filename"),
            release_version=_get(data, "releaseVersion", "version"),
            release_date=_get(data, "releaseDate", "publishedDate", "date"),
        )


@dataclass
class ConceptProfile(Record):
    concept: Optional[Concept] = None
    preferred_atom: Optional[Atom] = None
    definitions: List[Definition] = field(default_factory=list)
    relations: List[Relation] = field(default_factory=list)
    atoms: List[Atom] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ConceptProfile":
        concept = data.get("concept")
        preferred_atom = data.get("preferredAtom") or data.get("preferred_atom")
        definitions = data.get("definitions") or []
        relations = data.get("relations") or []
        atoms = data.get("atoms") or []
        return cls(
            raw=_as_dict(data),
            concept=Concept.from_dict(concept)
            if isinstance(concept, Mapping)
            else None,
            preferred_atom=Atom.from_dict(preferred_atom)
            if isinstance(preferred_atom, Mapping)
            else None,
            definitions=[
                Definition.from_dict(item)
                for item in definitions
                if isinstance(item, Mapping)
            ],
            relations=[
                Relation.from_dict(item)
                for item in relations
                if isinstance(item, Mapping)
            ],
            atoms=[Atom.from_dict(item) for item in atoms if isinstance(item, Mapping)],
        )


RecordFactory = Callable[[Mapping[str, Any]], T]


@dataclass
class UMLSResponse(Generic[T]):
    """Typed UMLS response envelope."""

    result: Any
    raw: Dict[str, Any]
    page_size: Optional[int] = None
    page_number: Optional[int] = None
    page_count: Optional[int] = None
    request_metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_payload(
        cls,
        payload: Mapping[str, Any],
        model: Optional[RecordFactory[T]] = None,
        request_metadata: Optional[Mapping[str, Any]] = None,
    ) -> "UMLSResponse[T]":
        raw = _as_dict(payload)
        result = raw.get("result")
        if result is None and isinstance(raw.get("releaseTypes"), list):
            result = raw["releaseTypes"]
        parsed: Any

        if isinstance(result, list):
            parsed = [_parse_item(item, model) for item in result]
        elif isinstance(result, dict) and isinstance(result.get("results"), list):
            parsed = [_parse_item(item, model) for item in result["results"]]
        elif isinstance(result, dict):
            parsed = _parse_item(result, model)
        else:
            parsed = result

        return cls(
            result=parsed,
            raw=raw,
            page_size=_get(raw, "pageSize"),
            page_number=_get(raw, "pageNumber"),
            page_count=_get(raw, "pageCount"),
            request_metadata=_as_dict(request_metadata)
            if request_metadata is not None
            else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return dict(self.raw)

    def to_rdf(self) -> str:
        from umls_python_client.formatting import to_rdf

        return to_rdf(self.raw)

    def save(
        self,
        path: Union[str, Path],
        format: str = "json",
        overwrite: bool = False,
    ) -> Path:
        from umls_python_client.exports import save_payload

        return save_payload(self, path, format=format, overwrite=overwrite)


def _parse_item(
    item: Any,
    model: Optional[RecordFactory[T]] = None,
) -> Any:
    if not isinstance(item, Mapping):
        return item
    if model is not None:
        return model(item)
    return model_for_class_type(item).from_dict(item)


def model_for_class_type(data: Mapping[str, Any]) -> type[Record]:
    class_type = data.get("classType")
    if class_type == "Concept":
        return Concept
    if class_type == "Atom":
        return Atom
    if class_type == "SourceAtomCluster":
        return SourceAtomCluster
    if class_type == "Definition":
        return Definition
    if class_type in {"ConceptRelation", "AtomClusterRelation", "AtomRelation"}:
        return Relation
    if class_type == "Attribute":
        return Attribute
    if class_type in {"SemanticType", "SemanticNetworkRelation"}:
        return SemanticType
    if class_type == "RootSource":
        return RootSource
    if "ui" in data and "name" in data:
        return SearchResult
    return UnknownRecord
