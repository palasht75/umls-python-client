from __future__ import annotations

from pathlib import Path
from typing import Any, Optional, Union

from umls_python_client.async_apis import AsyncAPIBase
from umls_python_client.models import LicenseValidation, ReleaseInfo, UMLSResponse
from umls_python_client.uts_apis import (
    AUTH_VALIDATE_URL,
    DOWNLOAD_URL,
    RELEASES_URL,
    _download_path,
    _normalize_release_payload,
    _validation_payload_from_text,
)


class AsyncAuthAPI(AsyncAPIBase):
    async def validate_user(
        self,
        user_api_key: Optional[str] = None,
        validator_api_key: Optional[str] = None,
    ) -> UMLSResponse[LicenseValidation]:
        text = await self._transport.request_text(
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

    async def validate_api_key(
        self,
        api_key: Optional[str] = None,
        validator_api_key: Optional[str] = None,
    ) -> UMLSResponse[LicenseValidation]:
        return await self.validate_user(
            user_api_key=api_key,
            validator_api_key=validator_api_key,
        )


class AsyncReleaseAPI(AsyncAPIBase):
    async def list_releases(
        self,
        release_type: Optional[str] = None,
        current: Optional[bool] = None,
    ) -> UMLSResponse[ReleaseInfo]:
        payload = await self._transport.request(
            absolute_url=RELEASES_URL,
            params={"releaseType": release_type, "current": current},
            auth_required=False,
        )
        return UMLSResponse.from_payload(
            _normalize_release_payload(payload),
            model=ReleaseInfo.from_dict,
        )

    async def get_releases(self, **kwargs: Any) -> UMLSResponse[ReleaseInfo]:
        return await self.list_releases(**kwargs)

    async def download_file(
        self,
        url: str,
        path: Union[str, Path],
        overwrite: bool = False,
    ) -> Path:
        target = _download_path(url, Path(path))
        if target.exists() and not overwrite:
            raise FileExistsError("{0} already exists.".format(target))
        target.parent.mkdir(parents=True, exist_ok=True)
        content = await self._transport.request_bytes(
            absolute_url=DOWNLOAD_URL,
            params={"url": url},
            auth_required=True,
        )
        target.write_bytes(content)
        return target
