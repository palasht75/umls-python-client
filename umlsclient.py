import logging

from cuiAPI.cui_api import CUIAPI
from searchAPI.search_api import SearchAPI
from sourceAPI.source_api import SourceAPI
from semanticNetworkAPI.semantic_network_api import SemanticNetworkAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class UMLSClient:
    """
    UMLSClient is the main interface for interacting with multiple UMLS APIs including:
    - SearchAPI
    - SourceAPI
    - CUIAPI
    - (Future) Semantic Network and Crosswalk APIs

    This class organizes the APIs into namespaces for easy access.
    """

    def __init__(self, api_key: str, version: str = "current"):
        """
        Initialize the UMLSClient with the provided API key and version.
        Each API is accessible via its own namespace, like sourceAPI, searchAPI, cuiAPI.

        Args:
            api_key (str): UMLS API key required for authentication.
            version (str): UMLS version to use for API calls (default is "current").
        """
        # Initialize individual API clients as attributes
        self.searchAPI = SearchAPI(api_key, version)
        self.sourceAPI = SourceAPI(api_key, version)
        self.cuiAPI = CUIAPI(api_key, version)
        self.semanticNetworkAPI = SemanticNetworkAPI(api_key, version)  # Placeholder for future semantic network API
        self.crosswalkAPI = None  # Placeholder for future crosswalk API

        # Log the successful initialization of UMLSClient
        logger.info(
            "UMLSClient initialized with SearchAPI, SourceAPI, CUIAPI, and placeholders for future APIs."
        )
