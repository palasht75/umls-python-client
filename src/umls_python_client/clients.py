from __future__ import annotations

from typing import Optional

import httpx

from umls_python_client.apis import (
    CUIAPI,
    AtomAPI,
    CrosswalkAPI,
    MetadataAPI,
    SearchAPI,
    SemanticNetworkAPI,
    SourceAPI,
    TypedAtomAPI,
    TypedCrosswalkAPI,
    TypedCUIAPI,
    TypedMetadataAPI,
    TypedSearchAPI,
    TypedSemanticNetworkAPI,
    TypedSourceAPI,
)
from umls_python_client.async_apis import (
    AsyncAtomAPI,
    AsyncCrosswalkAPI,
    AsyncCUIAPI,
    AsyncMetadataAPI,
    AsyncSearchAPI,
    AsyncSemanticNetworkAPI,
    AsyncSourceAPI,
)
from umls_python_client.transport import AsyncUMLSTransport, SyncUMLSTransport


class UMLSClient:
    """Backward-compatible UMLS client."""

    def __init__(
        self,
        api_key: str,
        version: str = "current",
        timeout: float = 30.0,
        retries: int = 2,
        http_client: Optional[httpx.Client] = None,
        http_transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self._transport = SyncUMLSTransport(
            api_key=api_key,
            timeout=timeout,
            retries=retries,
            client=http_client,
            transport=http_transport,
        )
        self.version = version

        self.search_api = SearchAPI(version=version, transport=self._transport)
        self.source_api = SourceAPI(version=version, transport=self._transport)
        self.cui_api = CUIAPI(version=version, transport=self._transport)
        self.semantic_network_api = SemanticNetworkAPI(
            version=version, transport=self._transport
        )
        self.crosswalk_api = CrosswalkAPI(version=version, transport=self._transport)
        self.metadata_api = MetadataAPI(version=version, transport=self._transport)
        self.atom_api = AtomAPI(version=version, transport=self._transport)

        self.searchAPI = self.search_api
        self.sourceAPI = self.source_api
        self.cuiAPI = self.cui_api
        self.semanticNetworkAPI = self.semantic_network_api
        self.crosswalkAPI = self.crosswalk_api

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "UMLSClient":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()


class TypedUMLSClient:
    """Model-first synchronous UMLS client."""

    def __init__(
        self,
        api_key: str,
        version: str = "current",
        timeout: float = 30.0,
        retries: int = 2,
        http_client: Optional[httpx.Client] = None,
        http_transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        self._transport = SyncUMLSTransport(
            api_key=api_key,
            timeout=timeout,
            retries=retries,
            client=http_client,
            transport=http_transport,
        )
        self.version = version

        self.search_api = TypedSearchAPI(version=version, transport=self._transport)
        self.source_api = TypedSourceAPI(version=version, transport=self._transport)
        self.cui_api = TypedCUIAPI(version=version, transport=self._transport)
        self.semantic_network_api = TypedSemanticNetworkAPI(
            version=version, transport=self._transport
        )
        self.crosswalk_api = TypedCrosswalkAPI(
            version=version, transport=self._transport
        )
        self.metadata_api = TypedMetadataAPI(version=version, transport=self._transport)
        self.atom_api = TypedAtomAPI(version=version, transport=self._transport)

    def close(self) -> None:
        self._transport.close()

    def __enter__(self) -> "TypedUMLSClient":
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()


class AsyncUMLSClient:
    """Model-first asynchronous UMLS client."""

    def __init__(
        self,
        api_key: str,
        version: str = "current",
        timeout: float = 30.0,
        retries: int = 2,
        http_client: Optional[httpx.AsyncClient] = None,
        http_transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        self._transport = AsyncUMLSTransport(
            api_key=api_key,
            timeout=timeout,
            retries=retries,
            client=http_client,
            transport=http_transport,
        )
        self.version = version

        self.search_api = AsyncSearchAPI(version=version, transport=self._transport)
        self.source_api = AsyncSourceAPI(version=version, transport=self._transport)
        self.cui_api = AsyncCUIAPI(version=version, transport=self._transport)
        self.semantic_network_api = AsyncSemanticNetworkAPI(
            version=version, transport=self._transport
        )
        self.crosswalk_api = AsyncCrosswalkAPI(
            version=version, transport=self._transport
        )
        self.metadata_api = AsyncMetadataAPI(version=version, transport=self._transport)
        self.atom_api = AsyncAtomAPI(version=version, transport=self._transport)

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> "AsyncUMLSClient":
        return self

    async def __aexit__(self, *_exc_info: object) -> None:
        await self.aclose()
