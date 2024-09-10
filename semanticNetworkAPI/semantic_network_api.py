import requests
import logging
from baseAPI.umls_api_base import UMLSAPIBase

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()


class SemanticNetworkAPI(UMLSAPIBase):
    """
    A class to interact with the UMLS REST API's semantic network functionality, inheriting from UMLSAPIBase.

    The SemanticNetworkAPI class provides methods to retrieve semantic type information by its TUI (Type Unique Identifier).

    Attributes:
        api_key (str): The UMLS API key used for authentication (inherited from the UMLSAPIBase class).
        version (str): The version of the UMLS release to use (inherited from UMLSAPIBase).
    """

    def get_semantic_type(self, tui: str):
        """
        Retrieve information about a semantic type using its TUI (Type Unique Identifier).

        Args:
            tui (str): The TUI identifier for the semantic type you want to retrieve.

        Returns:
            dict: The semantic type information retrieved from the UMLS API.
        """
        # Construct the URL for the semantic network endpoint
        url = f"{self.base_url}/semantic-network/{self.version}/TUI/{tui}"
        params = {'apiKey': self.api_key}
        
        # Log the API request
        logger.info(f"Fetching semantic type for TUI: {tui}")

        # Make the API request
        try:
            response = requests.get(url, params=params)
        except requests.RequestException as e:
            logger.error(f"Error during API request: {e}")
            return {"error": f"Request failed: {e}"}

        # Handle the response
        return self._handle_response(response)
