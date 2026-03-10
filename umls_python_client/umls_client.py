import logging

from umls_python_client.crosswalkAPI.crosswalk_api import CrosswalkAPI
from umls_python_client.cuiAPI.cui_api import CUIAPI
from umls_python_client.searchAPI.search_api import SearchAPI
from umls_python_client.semanticNetworkAPI.semantic_network_api import (
    SemanticNetworkAPI,
)
from umls_python_client.sourceAPI.source_api import SourceAPI

logger = logging.getLogger(__name__)


class UMLSClient:
    """
    UMLSClient is the main interface for interacting with multiple UMLS APIs including:
    - SearchAPI
    - SourceAPI
    - CUIAPI
    - Semantic Network
    - Crosswalk APIs

    This class organizes the APIs into namespaces for easy access.
    """

    def __init__(self, api_key: str, version: str = "current", timeout: float = 30.0):
        """
        Initialize the UMLSClient with the provided API key and version.
        Each API is accessible via its own namespace, like sourceAPI, searchAPI, cuiAPI.

        Args:
            api_key (str): UMLS API key required for authentication.
            version (str): UMLS version to use for API calls (default is "current").
            timeout (float): Timeout in seconds for each HTTP request.
        """
        # Preferred snake_case API namespaces
        self.search_api = SearchAPI(api_key, version, timeout=timeout)
        self.source_api = SourceAPI(api_key, version, timeout=timeout)
        self.cui_api = CUIAPI(api_key, version, timeout=timeout)
        self.semantic_network_api = SemanticNetworkAPI(
            api_key, version, timeout=timeout
        )
        self.crosswalk_api = CrosswalkAPI(api_key, version, timeout=timeout)

        # Backwards-compatible aliases
        self.searchAPI = self.search_api
        self.sourceAPI = self.source_api
        self.cuiAPI = self.cui_api
        self.semanticNetworkAPI = self.semantic_network_api
        self.crosswalkAPI = self.crosswalk_api

        logger.info("UMLSClient initialized for version '%s'.", version)
