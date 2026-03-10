import logging
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

import requests

from umls_python_client.utils.save_output import save_output_to_file
from umls_python_client.utils.utils import handle_response_with_format

logger = logging.getLogger(__name__)

VALID_OUTPUT_FORMATS = {"json", "rdf"}


class UMLSAPIBase:
    """Common behavior for all UMLS API clients."""

    def __init__(
        self,
        api_key: str,
        version: str = "current",
        timeout: float = 30.0,
        session: Optional[requests.Session] = None,
    ) -> None:
        if not isinstance(api_key, str) or not api_key.strip():
            raise ValueError("A non-empty API key is required for UMLS API requests.")
        if timeout <= 0:
            raise ValueError("timeout must be a positive number.")

        self.api_key = api_key.strip()
        self.base_url = "https://uts-ws.nlm.nih.gov/rest"
        self.version = version
        self.timeout = timeout
        self.session = session or requests.Session()

    @staticmethod
    def _validate_format(output_format: str) -> None:
        if output_format not in VALID_OUTPUT_FORMATS:
            allowed = ", ".join(sorted(VALID_OUTPUT_FORMATS))
            raise ValueError(
                f"Invalid format '{output_format}'. Allowed formats: {allowed}."
            )

    @staticmethod
    def _format_json(data: Dict[str, Any]) -> str:
        return handle_response_with_format(data, format="json", return_indented=True)

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        if response.status_code == 200:
            try:
                payload = response.json()
            except ValueError:
                logger.exception("Response body is not valid JSON.")
                return {
                    "error": "Invalid JSON in response.",
                    "status_code": response.status_code,
                    "message": response.text,
                }
            if isinstance(payload, dict):
                return payload
            return {"result": payload}

        if response.status_code == 401:
            logger.error("Unauthorized request (401).")
            return {
                "error": "Invalid API Key. Please verify your key.",
                "status_code": response.status_code,
                "documentation_url": "https://documentation.uts.nlm.nih.gov/rest/authentication.html",
            }

        if response.status_code == 403:
            logger.error("Forbidden request (403).")
            return {
                "error": "Access denied. API key may lack required permissions.",
                "status_code": response.status_code,
            }

        if response.status_code == 404:
            logger.error("Resource not found (404).")
            return {
                "error": "Resource not found.",
                "status_code": response.status_code,
                "message": response.text,
            }

        logger.error(
            "API request failed with status code %s: %s",
            response.status_code,
            response.text,
        )
        return {
            "error": "API request failed.",
            "status_code": response.status_code,
            "message": response.text,
        }

    def _request(
        self,
        *,
        path: Optional[str] = None,
        absolute_url: Optional[str] = None,
        params: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        if bool(path) == bool(absolute_url):
            raise ValueError("Provide exactly one of `path` or `absolute_url`.")

        request_params: Dict[str, Any] = {"apiKey": self.api_key}
        if params:
            request_params.update({k: v for k, v in params.items() if v is not None})

        url = absolute_url or f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = self.session.get(url, params=request_params, timeout=self.timeout)
        except requests.RequestException as exc:
            logger.error("Error during API request to %s: %s", url, exc)
            return {"error": "Request failed.", "message": str(exc)}

        return self._handle_response(response)

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
    ) -> Any:
        self._validate_format(output_format)
        response_payload = self._request(
            path=path,
            absolute_url=absolute_url,
            params=params,
        )

        if save_to_file:
            if not default_file_name:
                raise ValueError(
                    "default_file_name is required when save_to_file is True."
                )
            save_output_to_file(
                response=response_payload,
                file_path=self._resolve_file_path(default_file_name, file_path),
            )

        return handle_response_with_format(
            response=response_payload,
            format=output_format,
            return_indented=return_indented,
        )
