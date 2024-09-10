import logging
import os
from umlsclient import UMLSClient


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

PATH = r"C:\Users\palas\OneDrive\Desktop\umls-apis\python-umls-apis\output"

# Fetch the API key from environment variables
API_KEY = os.getenv("API_KEY")

# Main function to demonstrate the SearchAPI functionality
if __name__ == "__main__":
    # Initialize your UMLS API key from environment or configuration
    api_key = API_KEY
    if not api_key:
        logger.error("API Key is missing. Please set it in your environment.")
        exit(1)

    crosswalk_api = UMLSClient(api_key).crosswalkAPI
    # Retrieve crosswalk data for a source and code
    crosswalk_data = crosswalk_api.get_crosswalk(
        source="HPO", 
        id="HP:0001947", 
        target_source="SNOMEDCT_US", 
        include_obsolete=False, 
        page_number=1, 
        page_size=10, 
        return_indented=True, 
        format="rdf"
    )

    print(crosswalk_data)
