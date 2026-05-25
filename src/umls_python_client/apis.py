from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import httpx

from umls_python_client.errors import UMLSError
from umls_python_client.formatting import render_payload, save_output_to_file
from umls_python_client.models import (
    Atom,
    Concept,
    Definition,
    Relation,
    RootSource,
    SearchResult,
    SemanticType,
    SourceAtomCluster,
    UMLSResponse,
)
from umls_python_client.transport import SyncUMLSTransport

logger = logging.getLogger(__name__)


class UMLSAPIBase:
    """Compatibility base class and shared sync endpoint helper."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        version: str = "current",
        timeout: float = 30.0,
        transport: Optional[SyncUMLSTransport] = None,
        http_client: Optional[httpx.Client] = None,
        http_transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self.version = version
        if transport is None:
            if api_key is None:
                raise ValueError("api_key is required when transport is not provided.")
            transport = SyncUMLSTransport(
                api_key=api_key,
                timeout=timeout,
                client=http_client,
                transport=http_transport,
            )
            self._owns_transport = True
        else:
            self._owns_transport = False
        self._transport = transport
        self.api_key = transport.api_key
        self.base_url = transport.base_url
        self.timeout = transport.timeout

    @staticmethod
    def _format_json(data: Dict[str, Any]) -> str:
        return json.dumps(data, indent=4)

    def _handle_response(self, response: Any) -> Dict[str, Any]:
        status_code = getattr(response, "status_code", None)
        text = getattr(response, "text", "")
        if status_code is not None and status_code >= 400:
            from umls_python_client.errors import UMLSHTTPError

            return UMLSHTTPError(status_code=status_code, message=text).to_dict()
        try:
            payload = response.json()
        except ValueError:
            return {
                "error": "Invalid JSON in response.",
                "status_code": status_code,
                "message": text,
            }
        return payload if isinstance(payload, dict) else {"result": payload}

    def _request(
        self,
        *,
        path: Optional[str] = None,
        absolute_url: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        auth_required: bool = True,
    ) -> Dict[str, Any]:
        try:
            return self._transport.request(
                path=path,
                absolute_url=absolute_url,
                params=params,
                auth_required=auth_required,
            )
        except UMLSError as exc:
            return exc.to_dict()

    @staticmethod
    def _resolve_file_path(default_file_name: str, file_path: Optional[str]) -> str:
        if not file_path:
            return default_file_name
        return str(Path(file_path) / default_file_name)

    def _request_formatted(
        self,
        *,
        path: Optional[str] = None,
        absolute_url: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        output_format: str = "json",
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        default_file_name: Optional[str] = None,
        auth_required: bool = True,
    ) -> Any:
        payload = self._request(
            path=path,
            absolute_url=absolute_url,
            params=params,
            auth_required=auth_required,
        )
        if save_to_file:
            if not default_file_name:
                raise ValueError("default_file_name is required for file output.")
            save_output_to_file(
                payload,
                self._resolve_file_path(default_file_name, file_path),
            )
        return render_payload(payload, output_format, return_indented)

    def _typed(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        model: Optional[Any] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
    ) -> UMLSResponse[Any]:
        payload = self._transport.request(
            path=path,
            params=params,
            absolute_url=absolute_url,
            auth_required=auth_required,
        )
        return UMLSResponse.from_payload(payload, model=model)

    def close(self) -> None:
        if self._owns_transport:
            self._transport.close()


class SearchAPI(UMLSAPIBase):
    """Backward-compatible Search API."""

    def search(
        self,
        search_string: str,
        input_type: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        return_id_type: str = "concept",
        sabs: Optional[str] = None,
        search_type: str = "words",
        partial_search: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        semantic_types: Optional[str] = None,
        semantic_groups: Optional[str] = None,
    ) -> Any:
        del page_number
        params = _search_params(
            search_string,
            input_type,
            include_obsolete,
            include_suppressible,
            return_id_type,
            sabs,
            search_type,
            partial_search,
            page_size,
            semantic_types,
            semantic_groups,
        )
        return self._request_formatted(
            path="/search/{0}".format(self.version),
            params=params,
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="search_{0}.txt".format(_safe_name(search_string)),
        )


class TypedSearchAPI(UMLSAPIBase):
    def search(
        self,
        search_string: str,
        input_type: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        return_id_type: str = "concept",
        sabs: Optional[str] = None,
        search_type: str = "words",
        partial_search: bool = False,
        page_size: int = 25,
        semantic_types: Optional[str] = None,
        semantic_groups: Optional[str] = None,
    ) -> UMLSResponse[SearchResult]:
        return self._typed(
            path="/search/{0}".format(self.version),
            params=_search_params(
                search_string,
                input_type,
                include_obsolete,
                include_suppressible,
                return_id_type,
                sabs,
                search_type,
                partial_search,
                page_size,
                semantic_types,
                semantic_groups,
            ),
            model=SearchResult.from_dict,
        )


class CUIAPI(UMLSAPIBase):
    """Backward-compatible CUI API."""

    def get_cui_info(
        self,
        cui: str,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        return self._request_formatted(
            path="/content/{0}/CUI/{1}".format(self.version, cui),
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="cui_info_{0}.txt".format(cui),
        )

    def get_atoms(
        self,
        cui: str,
        return_indented: bool = True,
        sabs: Optional[str] = None,
        ttys: Optional[str] = None,
        language: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 200,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        del page_number
        params = _atom_params(
            sabs, ttys, language, include_obsolete, include_suppressible, page_size
        )
        return self._request_formatted(
            path="/content/{0}/CUI/{1}/atoms".format(self.version, cui),
            params=params,
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="cui_atoms_{0}.txt".format(cui),
        )

    def get_preferred_atom(
        self,
        cui: str,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        return self._request_formatted(
            path="/content/{0}/CUI/{1}/atoms/preferred".format(self.version, cui),
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="cui_preferred_atom_{0}.txt".format(cui),
        )

    def get_definitions(
        self,
        cui: str,
        return_indented: bool = True,
        sabs: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 25,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        return self._request_formatted(
            path="/content/{0}/CUI/{1}/definitions".format(self.version, cui),
            params={"sabs": sabs, "pageNumber": page_number, "pageSize": page_size},
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="cui_definitions_{0}.txt".format(cui),
        )

    def get_relations(
        self,
        cui: str,
        return_indented: bool = True,
        sabs: Optional[str] = None,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        params = _relation_params(
            include_relation_labels,
            include_additional_labels,
            include_obsolete,
            include_suppressible,
            page_number,
            page_size,
            sabs=sabs,
        )
        return self._request_formatted(
            path="/content/{0}/CUI/{1}/relations".format(self.version, cui),
            params=params,
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="cui_relations_{0}.txt".format(cui),
        )


class TypedCUIAPI(UMLSAPIBase):
    def get_cui_info(self, cui: str) -> UMLSResponse[Concept]:
        return self._typed(
            path="/content/{0}/CUI/{1}".format(self.version, cui),
            model=Concept.from_dict,
        )

    def get_atoms(
        self,
        cui: str,
        sabs: Optional[str] = None,
        ttys: Optional[str] = None,
        language: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_size: int = 200,
    ) -> UMLSResponse[Atom]:
        return self._typed(
            path="/content/{0}/CUI/{1}/atoms".format(self.version, cui),
            params=_atom_params(
                sabs, ttys, language, include_obsolete, include_suppressible, page_size
            ),
            model=Atom.from_dict,
        )

    def get_preferred_atom(self, cui: str) -> UMLSResponse[Atom]:
        return self._typed(
            path="/content/{0}/CUI/{1}/atoms/preferred".format(self.version, cui),
            model=Atom.from_dict,
        )

    def get_definitions(
        self,
        cui: str,
        sabs: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 25,
    ) -> UMLSResponse[Definition]:
        return self._typed(
            path="/content/{0}/CUI/{1}/definitions".format(self.version, cui),
            params={"sabs": sabs, "pageNumber": page_number, "pageSize": page_size},
            model=Definition.from_dict,
        )

    def get_relations(
        self,
        cui: str,
        sabs: Optional[str] = None,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 25,
    ) -> UMLSResponse[Relation]:
        return self._typed(
            path="/content/{0}/CUI/{1}/relations".format(self.version, cui),
            params=_relation_params(
                include_relation_labels,
                include_additional_labels,
                include_obsolete,
                include_suppressible,
                page_number,
                page_size,
                sabs=sabs,
            ),
            model=Relation.from_dict,
        )


class SourceAPI(UMLSAPIBase):
    """Backward-compatible source-asserted API."""

    def get_source_concept(
        self,
        source: str,
        id: str,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._source_endpoint(
            source, id, None, return_indented, format, save_to_file, file_path
        )

    def get_source_atoms(
        self,
        source: str,
        id: str,
        sabs: Optional[str] = None,
        ttys: Optional[str] = None,
        language: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 200,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        del page_number
        params = _atom_params(
            sabs, ttys, language, include_obsolete, include_suppressible, page_size
        )
        return self._source_endpoint(
            source,
            id,
            "atoms",
            return_indented,
            format,
            save_to_file,
            file_path,
            params=params,
        )

    def get_source_preferred_atom(
        self,
        source: str,
        id: str,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._source_endpoint(
            source,
            id,
            "atoms/preferred",
            return_indented,
            format,
            save_to_file,
            file_path,
        )

    def get_source_parents(self, source: str, id: str, **kwargs: Any) -> Any:
        return self._source_endpoint_from_kwargs(source, id, "parents", kwargs)

    def get_source_children(self, source: str, id: str, **kwargs: Any) -> Any:
        return self._source_endpoint_from_kwargs(source, id, "children", kwargs)

    def get_source_ancestors(self, source: str, id: str, **kwargs: Any) -> Any:
        return self._source_endpoint_from_kwargs(source, id, "ancestors", kwargs)

    def get_source_descendants(self, source: str, id: str, **kwargs: Any) -> Any:
        return self._source_endpoint_from_kwargs(source, id, "descendants", kwargs)

    def get_source_attributes(
        self,
        source: str,
        id: str,
        include_attribute_names: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 200,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._source_endpoint(
            source,
            id,
            "attributes",
            return_indented,
            format,
            save_to_file,
            file_path,
            params={
                "includeAttributeNames": include_attribute_names,
                "pageNumber": page_number,
                "pageSize": page_size,
            },
        )

    def get_source_relations(
        self,
        source: str,
        id: str,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 200,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._source_endpoint(
            source,
            id,
            "relations",
            return_indented,
            format,
            save_to_file,
            file_path,
            params=_relation_params(
                include_relation_labels,
                include_additional_labels,
                include_obsolete,
                include_suppressible,
                page_number,
                page_size,
            ),
        )

    def get_relations_by_url(
        self,
        relations_url: str,
        return_indented: bool = True,
        format: str = "json",
    ) -> Any:
        return self._request_formatted(
            absolute_url=relations_url,
            output_format=format,
            return_indented=return_indented,
        )

    def get_concept_attributes(self, source: str, id: str) -> Dict[str, Any]:
        payload = _as_payload(
            self.get_source_attributes(source, id, return_indented=False)
        )
        attributes = payload.get("result", [])
        if not isinstance(attributes, list):
            return {}
        return {
            str(item.get("name")): item.get("value")
            for item in attributes
            if isinstance(item, dict) and item.get("name") and item.get("value")
        }

    def get_concept_pathways(
        self,
        source: str,
        id: str,
        max_depth: int = 2,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        pathways: Dict[str, Any] = {}
        queue = [(id, 0)]
        visited = set()
        while queue:
            concept_id, depth = queue.pop(0)
            if depth > max_depth or concept_id in visited:
                continue
            visited.add(concept_id)
            parents = _result_list(
                self.get_source_parents(source, concept_id, return_indented=False)
            )
            children = _result_list(
                self.get_source_children(source, concept_id, return_indented=False)
            )
            pathways["concept_{0}_parents".format(concept_id)] = [
                item.get("name") for item in parents if isinstance(item, dict)
            ]
            pathways["concept_{0}_children".format(concept_id)] = [
                item.get("name") for item in children if isinstance(item, dict)
            ]
            for item in parents + children:
                if isinstance(item, dict) and item.get("ui"):
                    queue.append((item["ui"], depth + 1))
        return _finalize_helper(
            pathways,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "concept_pathways_{0}_{1}.txt".format(source, id), file_path
            ),
        )

    def get_related_concepts_by_relation_type(
        self,
        source: str,
        id: str,
        relation_type: str,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        relations = _result_list(
            self.get_source_relations(source, id, return_indented=False)
        )
        related = [
            item.get("relatedIdName", "Unknown Concept")
            for item in relations
            if isinstance(item, dict)
            and item.get("relationLabel", "").lower() == relation_type.lower()
        ]
        payload = {relation_type: related}
        return _finalize_helper(
            payload,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "related_concepts_by_relation_type_{0}_{1}.txt".format(source, id),
                file_path,
            ),
        )

    def compare_concepts(
        self,
        source: str,
        id1: str,
        id2: str,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        first_ancestors = _result_list(
            self.get_source_ancestors(source, id1, return_indented=False)
        )
        second_ancestors = _result_list(
            self.get_source_ancestors(source, id2, return_indented=False)
        )
        first_descendants = _result_list(
            self.get_source_descendants(source, id1, return_indented=False)
        )
        second_descendants = _result_list(
            self.get_source_descendants(source, id2, return_indented=False)
        )
        payload = {
            "concept_1": id1,
            "concept_2": id2,
            "shared_ancestors": _shared_names(first_ancestors, second_ancestors),
            "shared_descendants": _shared_names(first_descendants, second_descendants),
        }
        return _finalize_helper(
            payload,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "compare_concepts_{0}_{1}_{2}.txt".format(source, id1, id2), file_path
            ),
        )

    def get_concept_coverage(
        self,
        source: str,
        id: str,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        payload = _as_payload(
            self.get_source_concept(source, id, return_indented=False)
        )
        result = payload.get("result", {})
        root_source = result.get("rootSource") if isinstance(result, dict) else None
        coverage = {"concept_id": id, "covered_in_sources": root_source}
        return _finalize_helper(
            coverage,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "concept_coverage_{0}_{1}.txt".format(source, id), file_path
            ),
        )

    def aggregate_children_by_attribute(
        self,
        source: str,
        id: str,
        attribute_name: str,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        aggregation: Dict[str, Any] = {}
        for child in _result_list(
            self.get_source_children(source, id, return_indented=False)
        ):
            if not isinstance(child, dict):
                continue
            child_id = child.get("ui")
            attributes = (
                self.get_concept_attributes(source, child_id) if child_id else {}
            )
            value = attributes.get(attribute_name, "Unknown")
            aggregation.setdefault(value, []).append(child.get("name"))
        return _finalize_helper(
            aggregation,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "children_by_attribute_{0}_{1}.txt".format(source, id), file_path
            ),
        )

    def get_family_tree(
        self,
        source: str,
        id: str,
        max_depth: int = 3,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        del max_depth
        concept = _as_payload(
            self.get_source_concept(source, id, return_indented=False)
        )
        result = concept.get("result", {})
        payload = {
            "concept_id": id,
            "concept_name": result.get("name") if isinstance(result, dict) else None,
            "ancestors": _result_list(
                self.get_source_ancestors(source, id, return_indented=False)
            ),
            "descendants": _result_list(
                self.get_source_descendants(source, id, return_indented=False)
            ),
        }
        return _finalize_helper(
            payload,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "family_tree_{0}_{1}.txt".format(source, id), file_path
            ),
        )

    def get_full_hierarchy_recursive(
        self,
        source: str,
        id: str,
        depth: int = 0,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        del depth
        payload = {
            "concept_id": id,
            "ancestors": _result_list(
                self.get_source_ancestors(source, id, return_indented=False)
            ),
            "descendants": _result_list(
                self.get_source_descendants(source, id, return_indented=False)
            ),
        }
        return _finalize_helper(
            payload,
            return_indented,
            save_to_file,
            self._resolve_file_path(
                "full_hierarchy_{0}_{1}.txt".format(source, id), file_path
            ),
        )

    def _source_endpoint_from_kwargs(
        self,
        source: str,
        id: str,
        suffix: str,
        kwargs: Dict[str, Any],
    ) -> Any:
        return self._source_endpoint(
            source,
            id,
            suffix,
            kwargs.pop("return_indented", True),
            kwargs.pop("format", "json"),
            kwargs.pop("save_to_file", False),
            kwargs.pop("file_path", None),
            params={"pageSize": kwargs.pop("page_size", None)},
        )

    def _source_endpoint(
        self,
        source: str,
        id: str,
        suffix: Optional[str],
        return_indented: bool,
        output_format: str,
        save_to_file: bool,
        file_path: Optional[str],
        params: Optional[Mapping[str, Any]] = None,
    ) -> Any:
        path = "/content/{0}/source/{1}/{2}".format(self.version, source, id)
        file_suffix = "concept" if suffix is None else suffix.replace("/", "_")
        if suffix:
            path = "{0}/{1}".format(path, suffix)
        return self._request_formatted(
            path=path,
            params=params,
            output_format=output_format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="source_{0}_{1}_{2}.txt".format(
                file_suffix, source, _safe_name(id)
            ),
        )


class TypedSourceAPI(UMLSAPIBase):
    def get_source_concept(
        self, source: str, id: str
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed(
            path="/content/{0}/source/{1}/{2}".format(self.version, source, id),
            model=SourceAtomCluster.from_dict,
        )

    def get_source_atoms(
        self,
        source: str,
        id: str,
        sabs: Optional[str] = None,
        ttys: Optional[str] = None,
        language: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_size: int = 200,
    ) -> UMLSResponse[Atom]:
        return self._typed(
            path="/content/{0}/source/{1}/{2}/atoms".format(self.version, source, id),
            params=_atom_params(
                sabs, ttys, language, include_obsolete, include_suppressible, page_size
            ),
            model=Atom.from_dict,
        )

    def get_source_preferred_atom(self, source: str, id: str) -> UMLSResponse[Atom]:
        return self._typed(
            path="/content/{0}/source/{1}/{2}/atoms/preferred".format(
                self.version, source, id
            ),
            model=Atom.from_dict,
        )

    def get_source_parents(
        self, source: str, id: str, page_size: int = 200
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed_source_list(source, id, "parents", page_size)

    def get_source_children(
        self, source: str, id: str, page_size: int = 200
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed_source_list(source, id, "children", page_size)

    def get_source_ancestors(
        self, source: str, id: str, page_size: int = 200
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed_source_list(source, id, "ancestors", page_size)

    def get_source_descendants(
        self, source: str, id: str, page_size: int = 200
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed_source_list(source, id, "descendants", page_size)

    def get_source_attributes(
        self,
        source: str,
        id: str,
        include_attribute_names: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 200,
    ) -> UMLSResponse[Any]:
        return self._typed(
            path="/content/{0}/source/{1}/{2}/attributes".format(
                self.version, source, id
            ),
            params={
                "includeAttributeNames": include_attribute_names,
                "pageNumber": page_number,
                "pageSize": page_size,
            },
        )

    def get_source_relations(
        self,
        source: str,
        id: str,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 200,
    ) -> UMLSResponse[Relation]:
        return self._typed(
            path="/content/{0}/source/{1}/{2}/relations".format(
                self.version, source, id
            ),
            params=_relation_params(
                include_relation_labels,
                include_additional_labels,
                include_obsolete,
                include_suppressible,
                page_number,
                page_size,
            ),
            model=Relation.from_dict,
        )

    def _typed_source_list(
        self,
        source: str,
        id: str,
        suffix: str,
        page_size: int,
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed(
            path="/content/{0}/source/{1}/{2}/{3}".format(
                self.version, source, id, suffix
            ),
            params={"pageSize": page_size},
            model=SourceAtomCluster.from_dict,
        )


class AtomAPI(UMLSAPIBase):
    def get_atom(
        self,
        aui: str,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._atom_endpoint(
            aui, None, return_indented, format, save_to_file, file_path
        )

    def get_parents(self, aui: str, **kwargs: Any) -> Any:
        return self._atom_endpoint_from_kwargs(aui, "parents", kwargs)

    def get_children(self, aui: str, **kwargs: Any) -> Any:
        return self._atom_endpoint_from_kwargs(aui, "children", kwargs)

    def get_ancestors(self, aui: str, **kwargs: Any) -> Any:
        return self._atom_endpoint_from_kwargs(aui, "ancestors", kwargs)

    def get_descendants(self, aui: str, **kwargs: Any) -> Any:
        return self._atom_endpoint_from_kwargs(aui, "descendants", kwargs)

    def _atom_endpoint_from_kwargs(
        self, aui: str, suffix: str, kwargs: Dict[str, Any]
    ) -> Any:
        return self._atom_endpoint(
            aui,
            suffix,
            kwargs.pop("return_indented", True),
            kwargs.pop("format", "json"),
            kwargs.pop("save_to_file", False),
            kwargs.pop("file_path", None),
            page_size=kwargs.pop("page_size", 200),
        )

    def _atom_endpoint(
        self,
        aui: str,
        suffix: Optional[str],
        return_indented: bool,
        output_format: str,
        save_to_file: bool,
        file_path: Optional[str],
        page_size: Optional[int] = None,
    ) -> Any:
        path = "/content/{0}/AUI/{1}".format(self.version, aui)
        file_suffix = "atom" if suffix is None else suffix
        if suffix:
            path = "{0}/{1}".format(path, suffix)
        return self._request_formatted(
            path=path,
            params={"pageSize": page_size},
            output_format=output_format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="aui_{0}_{1}.txt".format(file_suffix, aui),
        )


class TypedAtomAPI(UMLSAPIBase):
    def get_atom(self, aui: str) -> UMLSResponse[Atom]:
        return self._typed(
            path="/content/{0}/AUI/{1}".format(self.version, aui),
            model=Atom.from_dict,
        )

    def get_parents(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return self._typed_atom_list(aui, "parents", page_size)

    def get_children(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return self._typed_atom_list(aui, "children", page_size)

    def get_ancestors(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return self._typed_atom_list(aui, "ancestors", page_size)

    def get_descendants(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return self._typed_atom_list(aui, "descendants", page_size)

    def _typed_atom_list(
        self, aui: str, suffix: str, page_size: int
    ) -> UMLSResponse[Atom]:
        return self._typed(
            path="/content/{0}/AUI/{1}/{2}".format(self.version, aui, suffix),
            params={"pageSize": page_size},
            model=Atom.from_dict,
        )


class CrosswalkAPI(UMLSAPIBase):
    def get_crosswalk(
        self,
        source: str,
        id: str,
        target_source: Optional[str] = None,
        include_obsolete: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._request_formatted(
            path="/crosswalk/{0}/source/{1}/{2}".format(self.version, source, id),
            params={
                "targetSource": target_source,
                "includeObsolete": include_obsolete,
                "pageNumber": page_number,
                "pageSize": page_size,
            },
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="crosswalk_{0}_{1}.txt".format(source, _safe_name(id)),
        )


class TypedCrosswalkAPI(UMLSAPIBase):
    def get_crosswalk(
        self,
        source: str,
        id: str,
        target_source: Optional[str] = None,
        include_obsolete: bool = False,
        page_number: int = 1,
        page_size: int = 25,
    ) -> UMLSResponse[SourceAtomCluster]:
        return self._typed(
            path="/crosswalk/{0}/source/{1}/{2}".format(self.version, source, id),
            params={
                "targetSource": target_source,
                "includeObsolete": include_obsolete,
                "pageNumber": page_number,
                "pageSize": page_size,
            },
            model=SourceAtomCluster.from_dict,
        )


class SemanticNetworkAPI(UMLSAPIBase):
    def get_semantic_type(
        self,
        tui: str,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        return_indented: bool = True,
        format: str = "json",
    ) -> Any:
        return self._request_formatted(
            path="/semantic-network/{0}/TUI/{1}".format(self.version, tui),
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="semantic_type_{0}.txt".format(tui),
        )


class TypedSemanticNetworkAPI(UMLSAPIBase):
    def get_semantic_type(self, tui: str) -> UMLSResponse[SemanticType]:
        return self._typed(
            path="/semantic-network/{0}/TUI/{1}".format(self.version, tui),
            model=SemanticType.from_dict,
        )


class MetadataAPI(UMLSAPIBase):
    def get_sources(
        self,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        return self._request_formatted(
            path="/metadata/{0}/sources".format(self.version),
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="metadata_sources.txt",
            auth_required=False,
        )


class TypedMetadataAPI(UMLSAPIBase):
    def get_sources(self) -> UMLSResponse[RootSource]:
        return self._typed(
            path="/metadata/{0}/sources".format(self.version),
            model=RootSource.from_dict,
            auth_required=False,
        )


def _search_params(
    search_string: str,
    input_type: Optional[str],
    include_obsolete: bool,
    include_suppressible: bool,
    return_id_type: str,
    sabs: Optional[str],
    search_type: str,
    partial_search: bool,
    page_size: int,
    semantic_types: Optional[str],
    semantic_groups: Optional[str],
) -> Dict[str, Any]:
    return {
        "string": search_string,
        "inputType": input_type,
        "includeObsolete": include_obsolete,
        "includeSuppressible": include_suppressible,
        "returnIdType": return_id_type,
        "sabs": sabs,
        "searchType": search_type,
        "partialSearch": partial_search,
        "pageSize": page_size,
        "semanticTypes": semantic_types,
        "semanticGroups": semantic_groups,
    }


def _atom_params(
    sabs: Optional[str],
    ttys: Optional[str],
    language: Optional[str],
    include_obsolete: bool,
    include_suppressible: bool,
    page_size: int,
) -> Dict[str, Any]:
    return {
        "sabs": sabs,
        "ttys": ttys,
        "language": language,
        "includeObsolete": include_obsolete,
        "includeSuppressible": include_suppressible,
        "pageSize": page_size,
    }


def _relation_params(
    include_relation_labels: Optional[str],
    include_additional_labels: Optional[str],
    include_obsolete: bool,
    include_suppressible: bool,
    page_number: int,
    page_size: int,
    sabs: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "sabs": sabs,
        "includeRelationLabels": include_relation_labels,
        "includeAdditionalRelationLabels": include_additional_labels,
        "includeObsolete": include_obsolete,
        "includeSuppressible": include_suppressible,
        "pageNumber": page_number,
        "pageSize": page_size,
    }


def _safe_name(value: str) -> str:
    return "".join(
        char if char.isalnum() or char in {"-", "_"} else "_" for char in value
    )


def _as_payload(value: Any) -> Dict[str, Any]:
    if isinstance(value, str):
        parsed = json.loads(value)
        return parsed if isinstance(parsed, dict) else {"result": parsed}
    return value if isinstance(value, dict) else {"result": value}


def _result_list(value: Any) -> list[Any]:
    payload = _as_payload(value)
    result = payload.get("result", [])
    return result if isinstance(result, list) else []


def _finalize_helper(
    payload: Dict[str, Any],
    return_indented: bool,
    save_to_file: bool,
    file_path: str,
) -> Any:
    if save_to_file:
        save_output_to_file(payload, file_path)
    if return_indented:
        return json.dumps(payload, indent=4)
    return payload


def _shared_names(first: list[Any], second: list[Any]) -> list[Any]:
    second_items = [item for item in second if isinstance(item, dict)]
    return [
        item.get("name")
        for item in first
        if isinstance(item, dict) and item in second_items
    ]
