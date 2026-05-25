from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


class UMLSError(Exception):
    """Base class for UMLS client errors."""

    def to_dict(self) -> Dict[str, Any]:
        return {"error": str(self)}


class UMLSRequestError(UMLSError):
    """Raised when the HTTP client cannot complete a request."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {"error": "Request failed.", "message": self.message}


@dataclass
class UMLSHTTPError(UMLSError):
    """Raised when UMLS returns a non-success HTTP status."""

    status_code: int
    message: str
    url: Optional[str] = None

    def __str__(self) -> str:
        return "UMLS request failed with status {0}: {1}".format(
            self.status_code, self.message
        )

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "error": "API request failed.",
            "status_code": self.status_code,
            "message": self.message,
        }
        if self.status_code == 401:
            payload.update(
                {
                    "error": "Invalid API Key. Please verify your key.",
                    "documentation_url": (
                        "https://documentation.uts.nlm.nih.gov/rest/authentication.html"
                    ),
                }
            )
        elif self.status_code == 403:
            payload["error"] = "Access denied. API key may lack required permissions."
        elif self.status_code == 404:
            payload["error"] = "Resource not found."
        if self.url:
            payload["url"] = self.url
        return payload


class UMLSDecodeError(UMLSError):
    """Raised when UMLS returns a response body that is not valid JSON."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "error": "Invalid JSON in response.",
            "message": self.message,
        }
        if self.status_code is not None:
            payload["status_code"] = self.status_code
        return payload
