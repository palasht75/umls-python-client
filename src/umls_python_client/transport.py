from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Dict, Mapping, Optional
from urllib.parse import urlparse

import httpx

from umls_python_client.errors import UMLSDecodeError, UMLSHTTPError, UMLSRequestError

logger = logging.getLogger(__name__)

DEFAULT_BASE_URL = "https://uts-ws.nlm.nih.gov/rest"
RETRY_STATUSES = {429, 500, 502, 503, 504}
TRUSTED_AUTH_HOSTS = {"uts-ws.nlm.nih.gov"}
SENSITIVE_METADATA_PARAMS = {"apikey", "validatorapikey"}


def clean_params(params: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
    cleaned: Dict[str, Any] = {}
    if not params:
        return cleaned
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            cleaned[key] = str(value).lower()
        elif isinstance(value, (list, tuple, set)):
            cleaned[key] = ",".join(str(item) for item in value)
        else:
            cleaned[key] = value
    return cleaned


def request_metadata(
    *,
    path: Optional[str] = None,
    absolute_url: Optional[str] = None,
    params: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    metadata: Dict[str, Any] = {}
    if path is not None:
        metadata["path"] = path
    if absolute_url is not None:
        metadata["absolute_url"] = absolute_url
    cleaned_params = {
        key: value
        for key, value in clean_params(params).items()
        if key.lower() not in SENSITIVE_METADATA_PARAMS
    }
    if cleaned_params:
        metadata["params"] = cleaned_params
    return metadata


class SyncUMLSTransport:
    """Synchronous UMLS HTTP transport."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        retries: int = 2,
        backoff_factor: float = 0.0,
        client: Optional[httpx.Client] = None,
        transport: Optional[httpx.BaseTransport] = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("A non-empty API key is required for UMLS API requests.")
        if timeout <= 0:
            raise ValueError("timeout must be a positive number.")
        if retries < 0:
            raise ValueError("retries must be zero or greater.")

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self._owns_client = client is None
        self.client = client or httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
        )

    def request(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
        follow_redirects: bool = False,
    ) -> Dict[str, Any]:
        return _decode_response(
            self._request_response(
                path, params, absolute_url, auth_required, follow_redirects
            )
        )

    def request_text(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
        follow_redirects: bool = False,
    ) -> str:
        response = self._request_response(
            path, params, absolute_url, auth_required, follow_redirects
        )
        if response.status_code >= 400:
            raise UMLSHTTPError(
                status_code=response.status_code,
                message=response.text,
                url=str(response.url),
            )
        return response.text

    def request_bytes(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
        follow_redirects: bool = False,
    ) -> bytes:
        response = self._request_response(
            path, params, absolute_url, auth_required, follow_redirects
        )
        if response.status_code >= 400:
            raise UMLSHTTPError(
                status_code=response.status_code,
                message=response.text,
                url=str(response.url),
            )
        return response.content

    def _request_response(
        self,
        path: Optional[str],
        params: Optional[Mapping[str, Any]],
        absolute_url: Optional[str],
        auth_required: bool,
        follow_redirects: bool,
    ) -> httpx.Response:
        if bool(path) == bool(absolute_url):
            raise ValueError("Provide exactly one of path or absolute_url.")
        request_params = clean_params(params)
        url = absolute_url or _normalize_path(path)
        if auth_required:
            _validate_authenticated_absolute_url(absolute_url, self.base_url)
            request_params["apiKey"] = self.api_key

        last_exc: Optional[httpx.RequestError] = None
        for attempt in range(self.retries + 1):
            try:
                response = self.client.get(
                    url,
                    params=request_params,
                    follow_redirects=follow_redirects,
                )
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt == self.retries:
                    raise UMLSRequestError(str(exc)) from exc
                _sleep(attempt, self.backoff_factor)
                continue

            if response.status_code in RETRY_STATUSES and attempt < self.retries:
                _sleep(attempt, self.backoff_factor)
                continue
            return response

        raise UMLSRequestError(str(last_exc) if last_exc else "Request failed.")

    def close(self) -> None:
        if self._owns_client:
            self.client.close()


class AsyncUMLSTransport:
    """Asynchronous UMLS HTTP transport."""

    def __init__(
        self,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 30.0,
        retries: int = 2,
        backoff_factor: float = 0.0,
        client: Optional[httpx.AsyncClient] = None,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("A non-empty API key is required for UMLS API requests.")
        if timeout <= 0:
            raise ValueError("timeout must be a positive number.")
        if retries < 0:
            raise ValueError("retries must be zero or greater.")

        self.api_key = api_key.strip()
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff_factor = backoff_factor
        self._owns_client = client is None
        self.client = client or httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            transport=transport,
        )

    async def request(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
        follow_redirects: bool = False,
    ) -> Dict[str, Any]:
        return _decode_response(
            await self._request_response(
                path, params, absolute_url, auth_required, follow_redirects
            )
        )

    async def request_text(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
        follow_redirects: bool = False,
    ) -> str:
        response = await self._request_response(
            path, params, absolute_url, auth_required, follow_redirects
        )
        if response.status_code >= 400:
            raise UMLSHTTPError(
                status_code=response.status_code,
                message=response.text,
                url=str(response.url),
            )
        return response.text

    async def request_bytes(
        self,
        path: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
        absolute_url: Optional[str] = None,
        auth_required: bool = True,
        follow_redirects: bool = False,
    ) -> bytes:
        response = await self._request_response(
            path, params, absolute_url, auth_required, follow_redirects
        )
        if response.status_code >= 400:
            raise UMLSHTTPError(
                status_code=response.status_code,
                message=response.text,
                url=str(response.url),
            )
        return response.content

    async def _request_response(
        self,
        path: Optional[str],
        params: Optional[Mapping[str, Any]],
        absolute_url: Optional[str],
        auth_required: bool,
        follow_redirects: bool,
    ) -> httpx.Response:
        if bool(path) == bool(absolute_url):
            raise ValueError("Provide exactly one of path or absolute_url.")
        request_params = clean_params(params)
        url = absolute_url or _normalize_path(path)
        if auth_required:
            _validate_authenticated_absolute_url(absolute_url, self.base_url)
            request_params["apiKey"] = self.api_key

        last_exc: Optional[httpx.RequestError] = None
        for attempt in range(self.retries + 1):
            try:
                response = await self.client.get(
                    url,
                    params=request_params,
                    follow_redirects=follow_redirects,
                )
            except httpx.RequestError as exc:
                last_exc = exc
                if attempt == self.retries:
                    raise UMLSRequestError(str(exc)) from exc
                await _async_sleep(attempt, self.backoff_factor)
                continue

            if response.status_code in RETRY_STATUSES and attempt < self.retries:
                await _async_sleep(attempt, self.backoff_factor)
                continue
            return response

        raise UMLSRequestError(str(last_exc) if last_exc else "Request failed.")

    async def aclose(self) -> None:
        if self._owns_client:
            await self.client.aclose()


def _normalize_path(path: Optional[str]) -> str:
    if path is None:
        raise ValueError("path is required.")
    return "/" + path.lstrip("/")


def _validate_authenticated_absolute_url(
    absolute_url: Optional[str],
    base_url: str,
) -> None:
    if absolute_url is None:
        return

    host = urlparse(absolute_url).hostname
    base_host = urlparse(base_url).hostname
    allowed_hosts = {
        allowed_host.lower()
        for allowed_host in (base_host, *TRUSTED_AUTH_HOSTS)
        if allowed_host
    }
    if not host or host.lower() not in allowed_hosts:
        display_host = host or "unknown host"
        raise UMLSRequestError(
            "Refusing to send UMLS API key to untrusted host: {0}.".format(display_host)
        )


def _decode_response(response: httpx.Response) -> Dict[str, Any]:
    if response.status_code >= 400:
        raise UMLSHTTPError(
            status_code=response.status_code,
            message=response.text,
            url=str(response.url),
        )
    try:
        payload = response.json()
    except ValueError as exc:
        raise UMLSDecodeError(str(exc), status_code=response.status_code) from exc
    if isinstance(payload, dict):
        return payload
    return {"result": payload}


def _sleep(attempt: int, backoff_factor: float) -> None:
    if backoff_factor <= 0:
        return
    time.sleep(backoff_factor * (2**attempt))


async def _async_sleep(attempt: int, backoff_factor: float) -> None:
    if backoff_factor <= 0:
        return
    await asyncio.sleep(backoff_factor * (2**attempt))
