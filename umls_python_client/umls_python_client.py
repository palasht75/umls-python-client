import logging

from .crosswalkAPI import CrosswalkAPI
from .cuiAPI import CUIAPI
from .searchAPI import SearchAPI
from .semanticNetworkAPI import SemanticNetworkAPI
from .sourceAPI import SourceAPI

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
    - Semantic Network
    - Crosswalk APIs

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
        self.semanticNetworkAPI = SemanticNetworkAPI(api_key, version)
        self.crosswalkAPI = CrosswalkAPI(api_key, version)

        # Log the successful initialization of UMLSClient
        logger.info(
            "UMLSClient initialized with SearchAPI, SourceAPI, CUIAPI, semanticNetworkAPI and crosswalkAPI"
        )
