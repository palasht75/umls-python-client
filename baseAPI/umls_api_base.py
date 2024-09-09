import logging
from typing import Any, Dict, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class UMLSAPIBase:
    """
    Base class for handling common functionality for UMLS APIs (CUI, Source, Crosswalk, etc.).

    Attributes:
        api_key (str): The API key used for making requests to the UMLS API.
        version (str): The version of the UMLS content to use, defaults to "current".
        base_url (str): The base URL for the UMLS API.
    """

    def __init__(self, api_key: str, version: str = "current"):
        """
        Initialize the UMLSAPIBase class with the API key and version.

        Args:
            api_key (str): The API key required for all API requests.
            version (str, optional): The version of the UMLS release to use. Defaults to "current".

        Raises:
            ValueError: If the API key is not provided or is empty.
        """
        if not api_key:
            raise ValueError("API key is required for UMLS API requests.")

        self.api_key = api_key
        self.base_url = "https://uts-ws.nlm.nih.gov/rest"
        self.version = version

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle the response from an API request.

        Args:
            response (requests.Response): The HTTP response from the API request.

        Returns:
            Dict[str, Any]: The parsed JSON response if the request is successful.
            Otherwise, returns a structured error message.
        """
        if response.status_code == 200:
            try:
                return response.json()
            except ValueError as e:
                logger.error(f"Error parsing JSON response: {e}")
                return {"error": "Error parsing JSON response."}

        # Check for unauthorized (invalid API key)
        if response.status_code == 401:
            logger.error("Invalid API Key detected.")
            return {
                "error": "Invalid API Key. Please verify your API key and try again.",
                "resolution": "Visit the UMLS API documentation for further details on how to obtain or renew your API key.",
                "documentation_url": "https://documentation.uts.nlm.nih.gov/rest/authentication.html",
            }

        # Other non-200 status codes
        logger.error(
            f"API request failed with status code {response.status_code}: {response.text}"
        )
        return {"error": "API request failed.", "message": response.text}

    def make_request(
        self, endpoint: str, params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make a GET request to the UMLS API with the given endpoint and parameters.

        Args:
            endpoint (str): The API endpoint to call, e.g., "/content/current/CUI/C0004238".
            params (Dict[str, str], optional): The query parameters for the request. Defaults to None.

        Returns:
            Dict[str, Any]: The parsed JSON response from the API.
        """
        url = f"{self.base_url}/{endpoint}"
        params = params or {}
        params["apiKey"] = self.api_key

        logger.info(f"Making API request to: {url} with params: {params}")

        try:
            response = requests.get(url, params=params)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": f"Request failed: {e}"}
