from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Optional, Union
from urllib.parse import urlparse

from umls_python_client.apis import UMLSAPIBase
from umls_python_client.errors import UMLSError
from umls_python_client.exports import save_payload
from umls_python_client.formatting import render_payload
from umls_python_client.models import LicenseValidation, ReleaseInfo, UMLSResponse

AUTH_VALIDATE_URL = "https://utslogin.nlm.nih.gov/validateUser"
DOWNLOAD_URL = "https://uts-ws.nlm.nih.gov/download"
RELEASES_URL = "https://uts-ws.nlm.nih.gov/releases"


class AuthAPI(UMLSAPIBase):
    """Backward-compatible UMLS license validation helper."""

    def validate_user(
        self,
        user_api_key: Optional[str] = None,
        validator_api_key: Optional[str] = None,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        payload = self._validation_payload(user_api_key, validator_api_key)
        if save_to_file:
            save_payload(
                payload,
                self._resolve_file_path("license_validation.txt", file_path),
                format="json",
                overwrite=True,
            )
        return render_payload(payload, format, return_indented)

    def validate_api_key(self, api_key: Optional[str] = None, **kwargs: Any) -> Any:
        return self.validate_user(user_api_key=api_key, **kwargs)

    def _validation_payload(
        self,
        user_api_key: Optional[str],
        validator_api_key: Optional[str],
    ) -> dict[str, Any]:
        try:
            text = self._transport.request_text(
                absolute_url=AUTH_VALIDATE_URL,
                params={
                    "validatorApiKey": validator_api_key or self.api_key,
                    "apiKey": user_api_key or self.api_key,
                },
                auth_required=False,
            )
        except UMLSError as exc:
            payload = exc.to_dict()
            payload["valid"] = False
            return payload
        return _validation_payload_from_text(text)


class TypedAuthAPI(UMLSAPIBase):
    def validate_user(
        self,
        user_api_key: Optional[str] = None,
        validator_api_key: Optional[str] = None,
    ) -> UMLSResponse[LicenseValidation]:
        text = self._transport.request_text(
            absolute_url=AUTH_VALIDATE_URL,
            params={
                "validatorApiKey": validator_api_key or self.api_key,
                "apiKey": user_api_key or self.api_key,
            },
            auth_required=False,
        )
        payload = _validation_payload_from_text(text)
        return UMLSResponse.from_payload(
            {"result": payload},
            model=LicenseValidation.from_dict,
        )

    def validate_api_key(
        self,
        api_key: Optional[str] = None,
        validator_api_key: Optional[str] = None,
    ) -> UMLSResponse[LicenseValidation]:
        return self.validate_user(
            user_api_key=api_key,
            validator_api_key=validator_api_key,
        )


class ReleaseAPI(UMLSAPIBase):
    """Backward-compatible release listing and download helper."""

    def list_releases(
        self,
        release_type: Optional[str] = None,
        current: Optional[bool] = None,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        format: str = "json",
    ) -> Any:
        return self._request_formatted(
            absolute_url=RELEASES_URL,
            params={"releaseType": release_type, "current": current},
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name="umls_releases.txt",
            auth_required=False,
        )

    def get_releases(self, **kwargs: Any) -> Any:
        return self.list_releases(**kwargs)

    def download_file(
        self,
        url: str,
        path: Union[str, Path],
        overwrite: bool = False,
    ) -> Path:
        target = _download_path(url, Path(path))
        if target.exists() and not overwrite:
            raise FileExistsError("{0} already exists.".format(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        content = self._transport.request_bytes(
            absolute_url=DOWNLOAD_URL,
            params={"url": url},
            auth_required=True,
        )
        target.write_bytes(content)
        return target


class TypedReleaseAPI(UMLSAPIBase):
    def list_releases(
        self,
        release_type: Optional[str] = None,
        current: Optional[bool] = None,
    ) -> UMLSResponse[ReleaseInfo]:
        payload = self._transport.request(
            absolute_url=RELEASES_URL,
            params={"releaseType": release_type, "current": current},
            auth_required=False,
        )
        return UMLSResponse.from_payload(
            _normalize_release_payload(payload),
            model=ReleaseInfo.from_dict,
        )

    def get_releases(self, **kwargs: Any) -> UMLSResponse[ReleaseInfo]:
        return self.list_releases(**kwargs)

    def download_file(
        self,
        url: str,
        path: Union[str, Path],
        overwrite: bool = False,
    ) -> Path:
        target = _download_path(url, Path(path))
        if target.exists() and not overwrite:
            raise FileExistsError("{0} already exists.".format(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        content = self._transport.request_bytes(
            absolute_url=DOWNLOAD_URL,
            params={"url": url},
            auth_required=True,
        )
        target.write_bytes(content)
        return target


def _validation_payload_from_text(text: str) -> dict[str, Any]:
    stripped = text.strip()
    try:
        parsed = json.loads(stripped)
    except ValueError:
        valid = stripped.lower() in {"true", "valid", "1", "yes"}
        return {"valid": valid, "message": stripped}
    if isinstance(parsed, Mapping):
        payload = dict(parsed)
        payload.setdefault(
            "valid", _truthy(payload.get("valid", payload.get("result")))
        )
        return payload
    return {"valid": _truthy(parsed), "message": stripped}


def _normalize_release_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(payload.get("releaseTypes"), list):
        normalized = dict(payload)
        normalized["result"] = payload["releaseTypes"]
        return normalized
    return dict(payload)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in {"true", "valid", "1", "yes"}
    return bool(value)


def _download_path(url: str, path: Path) -> Path:
    if path.exists() and path.is_dir():
        parsed = urlparse(url)
        name = Path(parsed.path).name or "umls_download"
        return path / name
    if path.suffix:
        return path
    parsed = urlparse(url)
    name = Path(parsed.path).name or "umls_download"
    return path / name
