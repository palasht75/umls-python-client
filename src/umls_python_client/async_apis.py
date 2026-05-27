from __future__ import annotations

from typing import Any, AsyncIterator, Dict, Iterable, Mapping, Optional

import httpx

from umls_python_client.models import (
    Atom,
    Attribute,
    Concept,
    ConceptProfile,
    Definition,
    Relation,
    RootSource,
    SearchResult,
    SemanticType,
    SourceAtomCluster,
    UMLSResponse,
)
from umls_python_client.transport import AsyncUMLSTransport, request_metadata


class AsyncAPIBase:
    def __init__(
        self,
        api_key: Optional[str] = None,
        version: str = "current",
        timeout: float = 30.0,
        transport: Optional[AsyncUMLSTransport] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        http_transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self.version = version
        if transport is None:
            if api_key is None:
                raise ValueError("api_key is required when transport is not provided.")
            transport = AsyncUMLSTransport(
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

    async def _typed(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        model: Optional[Any] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
    ) -> UMLSResponse[Any]:
        payload = await self._transport.request(
            path=path,
            params=params,
            absolute_url=absolute_url,
            auth_required=auth_required,
        )
        return UMLSResponse.from_payload(
            payload,
            model=model,
            request_metadata=request_metadata(
                path=path,
                absolute_url=absolute_url,
                params=params,
            ),
        )

    async def aclose(self) -> None:
        if self._owns_transport:
            await self._transport.aclose()


class AsyncSearchAPI(AsyncAPIBase):
    async def search(
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
        return await self._typed(
            path="/search/{0}".format(self.version),
            params={
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
            },
            model=SearchResult.from_dict,
        )

    async def bulk_search(
        self,
        search_strings: Iterable[str],
        **search_kwargs: Any,
    ) -> Dict[str, UMLSResponse[SearchResult]]:
        results: Dict[str, UMLSResponse[SearchResult]] = {}
        for search_string in search_strings:
            results[search_string] = await self.search(search_string, **search_kwargs)
        return results


class AsyncCUIAPI(AsyncAPIBase):
    async def get_cui_info(self, cui: str) -> UMLSResponse[Concept]:
        return await self._typed(
            path="/content/{0}/CUI/{1}".format(self.version, cui),
            model=Concept.from_dict,
        )

    async def get_atoms(
        self,
        cui: str,
        sabs: Optional[str] = None,
        ttys: Optional[str] = None,
        language: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_size: int = 200,
    ) -> UMLSResponse[Atom]:
        return await self._typed(
            path="/content/{0}/CUI/{1}/atoms".format(self.version, cui),
            params=_atom_params(
                sabs, ttys, language, include_obsolete, include_suppressible, page_size
            ),
            model=Atom.from_dict,
        )

    async def get_preferred_atom(self, cui: str) -> UMLSResponse[Atom]:
        return await self._typed(
            path="/content/{0}/CUI/{1}/atoms/preferred".format(self.version, cui),
            model=Atom.from_dict,
        )

    async def get_definitions(
        self,
        cui: str,
        sabs: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 25,
    ) -> UMLSResponse[Definition]:
        return await self._typed(
            path="/content/{0}/CUI/{1}/definitions".format(self.version, cui),
            params={"sabs": sabs, "pageNumber": page_number, "pageSize": page_size},
            model=Definition.from_dict,
        )

    async def get_relations(
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
        return await self._typed(
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

    async def get_concept_profile(
        self,
        cui: str,
        include_atoms: bool = False,
        include_definitions: bool = True,
        include_relations: bool = True,
        *,
        all_pages: bool = True,
        definitions_page_size: int = 25,
        relations_page_size: int = 25,
    ) -> UMLSResponse[ConceptProfile]:
        profile_payload: Dict[str, Any] = {
            "concept": _response_payload_result(await self.get_cui_info(cui)),
            "preferredAtom": _response_payload_result(
                await self.get_preferred_atom(cui)
            ),
            "definitions": [],
            "relations": [],
            "atoms": [],
        }
        if include_definitions:
            if all_pages:
                profile_payload["definitions"] = [
                    item.to_dict()
                    async for item in self.iter_definitions(
                        cui,
                        page_size=definitions_page_size,
                    )
                ]
            else:
                profile_payload["definitions"] = _response_payload_result(
                    await self.get_definitions(
                        cui,
                        page_size=definitions_page_size,
                    )
                )
        if include_relations:
            if all_pages:
                profile_payload["relations"] = [
                    item.to_dict()
                    async for item in self.iter_relations(
                        cui,
                        page_size=relations_page_size,
                    )
                ]
            else:
                profile_payload["relations"] = _response_payload_result(
                    await self.get_relations(
                        cui,
                        page_size=relations_page_size,
                    )
                )
        if include_atoms:
            profile_payload["atoms"] = _response_payload_result(
                await self.get_atoms(cui)
            )
        return UMLSResponse(
            result=ConceptProfile.from_dict(profile_payload),
            raw={"result": profile_payload},
            request_metadata=request_metadata(
                path="/content/{0}/CUI/{1}".format(self.version, cui),
                params={
                    "profile": True,
                    "allPages": all_pages,
                    "includeAtoms": include_atoms,
                    "includeDefinitions": include_definitions,
                    "includeRelations": include_relations,
                },
            ),
        )

    async def iter_definitions(
        self,
        cui: str,
        sabs: Optional[str] = None,
        page_size: int = 25,
    ) -> AsyncIterator[Definition]:
        async for item in _async_iter_paginated(
            lambda page_number: self.get_definitions(
                cui,
                sabs=sabs,
                page_number=page_number,
                page_size=page_size,
            )
        ):
            yield item

    async def iter_relations(
        self,
        cui: str,
        sabs: Optional[str] = None,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_size: int = 200,
    ) -> AsyncIterator[Relation]:
        async for item in _async_iter_paginated(
            lambda page_number: self.get_relations(
                cui,
                sabs=sabs,
                include_relation_labels=include_relation_labels,
                include_additional_labels=include_additional_labels,
                include_obsolete=include_obsolete,
                include_suppressible=include_suppressible,
                page_number=page_number,
                page_size=page_size,
            )
        ):
            yield item


class AsyncSourceAPI(AsyncAPIBase):
    async def get_source_concept(
        self, source: str, id: str
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._typed(
            path="/content/{0}/source/{1}/{2}".format(self.version, source, id),
            model=SourceAtomCluster.from_dict,
        )

    async def get_source_atoms(
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
        return await self._typed(
            path="/content/{0}/source/{1}/{2}/atoms".format(self.version, source, id),
            params=_atom_params(
                sabs, ttys, language, include_obsolete, include_suppressible, page_size
            ),
            model=Atom.from_dict,
        )

    async def get_source_preferred_atom(
        self, source: str, id: str
    ) -> UMLSResponse[Atom]:
        return await self._typed(
            path="/content/{0}/source/{1}/{2}/atoms/preferred".format(
                self.version, source, id
            ),
            model=Atom.from_dict,
        )

    async def get_source_parents(
        self, source: str, id: str, page_number: int = 1, page_size: int = 25
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._source_list(source, id, "parents", page_number, page_size)

    async def get_source_children(
        self, source: str, id: str, page_number: int = 1, page_size: int = 25
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._source_list(source, id, "children", page_number, page_size)

    async def get_source_ancestors(
        self, source: str, id: str, page_number: int = 1, page_size: int = 200
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._source_list(source, id, "ancestors", page_number, page_size)

    async def get_source_descendants(
        self, source: str, id: str, page_number: int = 1, page_size: int = 200
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._source_list(
            source, id, "descendants", page_number, page_size
        )

    async def get_source_attributes(
        self,
        source: str,
        id: str,
        include_attribute_names: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 25,
    ) -> UMLSResponse[Attribute]:
        return await self._typed(
            path="/content/{0}/source/{1}/{2}/attributes".format(
                self.version, source, id
            ),
            params={
                "includeAttributeNames": include_attribute_names,
                "pageNumber": page_number,
                "pageSize": page_size,
            },
            model=Attribute.from_dict,
        )

    async def get_source_relations(
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
        return await self._typed(
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

    async def iter_source_attributes(
        self,
        source: str,
        id: str,
        include_attribute_names: Optional[str] = None,
        page_size: int = 25,
    ) -> AsyncIterator[Attribute]:
        async for item in _async_iter_paginated(
            lambda page_number: self.get_source_attributes(
                source,
                id,
                include_attribute_names=include_attribute_names,
                page_number=page_number,
                page_size=page_size,
            )
        ):
            yield item

    async def iter_source_relations(
        self,
        source: str,
        id: str,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_size: int = 200,
    ) -> AsyncIterator[Relation]:
        async for item in _async_iter_paginated(
            lambda page_number: self.get_source_relations(
                source,
                id,
                include_relation_labels=include_relation_labels,
                include_additional_labels=include_additional_labels,
                include_obsolete=include_obsolete,
                include_suppressible=include_suppressible,
                page_number=page_number,
                page_size=page_size,
            )
        ):
            yield item

    async def _source_list(
        self, source: str, id: str, suffix: str, page_number: int, page_size: int
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._typed(
            path="/content/{0}/source/{1}/{2}/{3}".format(
                self.version, source, id, suffix
            ),
            params={"pageNumber": page_number, "pageSize": page_size},
            model=SourceAtomCluster.from_dict,
        )


class AsyncAtomAPI(AsyncAPIBase):
    async def get_atom(self, aui: str) -> UMLSResponse[Atom]:
        return await self._typed(
            path="/content/{0}/AUI/{1}".format(self.version, aui),
            model=Atom.from_dict,
        )

    async def get_parents(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return await self._atom_list(aui, "parents", page_size)

    async def get_children(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return await self._atom_list(aui, "children", page_size)

    async def get_ancestors(self, aui: str, page_size: int = 200) -> UMLSResponse[Atom]:
        return await self._atom_list(aui, "ancestors", page_size)

    async def get_descendants(
        self, aui: str, page_size: int = 200
    ) -> UMLSResponse[Atom]:
        return await self._atom_list(aui, "descendants", page_size)

    async def _atom_list(
        self, aui: str, suffix: str, page_size: int
    ) -> UMLSResponse[Atom]:
        return await self._typed(
            path="/content/{0}/AUI/{1}/{2}".format(self.version, aui, suffix),
            params={"pageSize": page_size},
            model=Atom.from_dict,
        )


class AsyncCrosswalkAPI(AsyncAPIBase):
    async def get_crosswalk(
        self,
        source: str,
        id: str,
        target_source: Optional[str] = None,
        include_obsolete: bool = False,
        page_number: int = 1,
        page_size: int = 25,
    ) -> UMLSResponse[SourceAtomCluster]:
        return await self._typed(
            path="/crosswalk/{0}/source/{1}/{2}".format(self.version, source, id),
            params={
                "targetSource": target_source,
                "includeObsolete": include_obsolete,
                "pageNumber": page_number,
                "pageSize": page_size,
            },
            model=SourceAtomCluster.from_dict,
        )

    async def bulk_crosswalk(
        self,
        identifiers: Iterable[str],
        source: str,
        target_source: Optional[str] = None,
        include_obsolete: bool = False,
        page_size: int = 25,
    ) -> Dict[str, UMLSResponse[SourceAtomCluster]]:
        results: Dict[str, UMLSResponse[SourceAtomCluster]] = {}
        for identifier in identifiers:
            results[identifier] = await self.get_crosswalk(
                source,
                identifier,
                target_source=target_source,
                include_obsolete=include_obsolete,
                page_size=page_size,
            )
        return results

    async def iter_crosswalk(
        self,
        source: str,
        id: str,
        target_source: Optional[str] = None,
        include_obsolete: bool = False,
        page_size: int = 25,
    ) -> AsyncIterator[SourceAtomCluster]:
        async for item in _async_iter_paginated(
            lambda page_number: self.get_crosswalk(
                source,
                id,
                target_source=target_source,
                include_obsolete=include_obsolete,
                page_number=page_number,
                page_size=page_size,
            )
        ):
            yield item


class AsyncSemanticNetworkAPI(AsyncAPIBase):
    async def get_semantic_type(self, tui: str) -> UMLSResponse[SemanticType]:
        return await self._typed(
            path="/semantic-network/{0}/TUI/{1}".format(self.version, tui),
            model=SemanticType.from_dict,
        )


class AsyncMetadataAPI(AsyncAPIBase):
    async def get_sources(self) -> UMLSResponse[RootSource]:
        return await self._typed(
            path="/metadata/{0}/sources".format(self.version),
            model=RootSource.from_dict,
            auth_required=False,
        )

    async def find_source(
        self,
        abbreviation: Optional[str] = None,
        name: Optional[str] = None,
    ) -> UMLSResponse[RootSource]:
        response = await self.get_sources()
        sources = _response_result_list(response)
        matched = [
            source
            for source in sources
            if isinstance(source, RootSource)
            and _source_matches(
                source.to_dict(),
                abbreviation=abbreviation,
                name=name,
            )
        ]
        return UMLSResponse(
            result=matched,
            raw={"result": [source.to_dict() for source in matched]},
            page_size=len(matched),
            page_number=1,
            page_count=1,
        )


def _payload_result(value: Mapping[str, Any]) -> Any:
    result = value.get("result")
    if isinstance(result, Mapping) and isinstance(result.get("results"), list):
        return result["results"]
    return result


def _response_payload_result(response: UMLSResponse[Any]) -> Any:
    return _payload_result(response.to_dict())


def _response_result_list(response: UMLSResponse[Any]) -> list[Any]:
    result = response.result
    if isinstance(result, list):
        return result
    if result is None:
        return []
    return [result]


async def _async_iter_paginated(fetch_page: Any) -> AsyncIterator[Any]:
    page_number = 1
    while True:
        response = await fetch_page(page_number)
        for item in _response_result_list(response):
            yield item
        if not response.page_count or page_number >= response.page_count:
            break
        page_number += 1


def _source_matches(
    source: Mapping[str, Any],
    abbreviation: Optional[str],
    name: Optional[str],
) -> bool:
    if abbreviation is None and name is None:
        return True
    if abbreviation is not None:
        source_abbreviation = source.get("abbreviation")
        if (
            isinstance(source_abbreviation, str)
            and source_abbreviation.lower() == abbreviation.lower()
        ):
            return True
    if name is None:
        return False
    needle = name.lower()
    for key in ("preferredName", "expandedForm", "shortName", "family"):
        value = source.get(key)
        if isinstance(value, str) and needle in value.lower():
            return True
    return False


def _atom_params(
    sabs: Optional[str],
    ttys: Optional[str],
    language: Optional[str],
    include_obsolete: bool,
    include_suppressible: bool,
    page_size: int,
) -> dict[str, Any]:
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
) -> dict[str, Any]:
    return {
        "sabs": sabs,
        "includeRelationLabels": include_relation_labels,
        "includeAdditionalRelationLabels": include_additional_labels,
        "includeObsolete": include_obsolete,
        "includeSuppressible": include_suppressible,
        "pageNumber": page_number,
        "pageSize": page_size,
    }
