import requests
import logging
from relationship_labels import RELATION_LABELS
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

class UMLSAPIBase:
    """Base class for common functionality like request handling."""
    
    def __init__(self, api_key, version="current"):
        self.api_key = api_key
        self.base_url = "https://uts-ws.nlm.nih.gov/rest"
        self.version = version

    def _handle_response(self, response):
        """Handle API responses."""
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return {"error": f"API request failed with status code {response.status_code}: {response.text}"}