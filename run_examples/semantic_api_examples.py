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

# Main function to demonstrate the SemanticNetworkAPI functionality
if __name__ == "__main__":
    # Initialize your UMLS API key from environment
    api_key = API_KEY
    if not api_key:
        logger.error("API Key is missing. Please set it in your environment.")
        exit(1)

    # Initialize the SemanticNetworkAPI class with your API key
    semantic_network_api = UMLSClient(api_key).semanticNetworkAPI

    #############################
    # Retrieve Semantic Type Information
    #############################
    logger.info("Fetching semantic type information for TUI 'T109':")
    tui = "T109"  # TUI for 'Anatomical Structure'
    file_name = f"semantic_network_{tui}.txt"
    semantic_type_info = semantic_network_api.get_semantic_type(tui, save_to_file=True, file_path=os.path.join(PATH,file_name))
    logger.info(f"Semantic Type Information for TUI {tui}: {semantic_type_info}")
    logger.info(f"Semantic Type Information for TUI {tui}: {semantic_type_info}")

    # #############################
    # # Retrieve Semantic Type Information for another TUI
    # #############################
    logger.info("Fetching semantic type information for TUI 'T121':")
    tui_2 = "T121"  # TUI for 'Pharmacologic Substance'
    semantic_type_info_2 = semantic_network_api.get_semantic_type(tui_2, format="rdf")
    logger.info(f"Semantic Type Information for TUI {tui_2}: {semantic_type_info_2}")
