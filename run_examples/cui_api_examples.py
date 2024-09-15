import logging
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from umls_python_client.umls_client import UMLSClient

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# PATH = r"C:\Users\palas\OneDrive\Desktop\umls-apis\python-umls-apis\output"
PATH = r"C:\Users\Shreya\Desktop\umls-apis\umls-python-client\output"

# Fetch the API key from environment variables
API_KEY = os.getenv("API_KEY")

# Main function to demonstrate the SearchAPI functionality
if __name__ == "__main__":
    # Initialize your UMLS API key from environment or configuration
    api_key = API_KEY
    if not api_key:
        logger.error("API Key is missing. Please set it in your environment.")
        exit(1)

    # Initialize the SearchAPI class with your API key
    cui_api = UMLSClient(api_key=api_key).cuiAPI

    #############################
    # Fetch CUI Information
    #############################
    logger.info("Fetching CUI information for 'C0011849':")
    cui_info = cui_api.get_cui_info(cui="C0011849", save_to_file=True, file_path=PATH)
    logger.info(f"CUI Information:\n{cui_info}")
    sys.stdout.flush()

    #############################
    # Fetch Atoms for a CUI
    #############################
    logger.info("Fetching atoms for CUI 'C0011849':")
    cui_atoms = cui_api.get_atoms(
        cui="C0011849",
        sabs="SNOMEDCT_US",
        ttys="PT",
        language=None,
        include_obsolete=False,
        include_suppressible=False,
        page_number=1,
        page_size=25,
        save_to_file=True,
        file_path=PATH,
    )
    logger.info(f"Atoms for CUI 'C0011849':\n{cui_atoms}")
    sys.stdout.flush()

    #############################
    # Fetch Definitions for a CUI
    #############################
    logger.info("Fetching definitions for CUI 'C0011849':")
    cui_definition = cui_api.get_definitions(
        cui="C0011849",
        sabs="SNOMEDCT_US",
        page_number=1,
        page_size=25,
        save_to_file=True,
        file_path=PATH,
    )
    logger.info(f"Definitions for CUI 'C0011849':\n{cui_definition}")
    sys.stdout.flush()

    #############################
    # Fetch Relations for a CUI
    #############################
    logger.info("Fetching relationships for CUI 'C0011849':")
    cui_definition = cui_api.get_relations(
        cui="C0011849",
        sabs="SNOMEDCT_US",
        include_relation_labels=None,
        include_additional_labels=None,
        include_obsolete=False,
        include_suppressible=False,
        page_number=1,
        page_size=25,
        save_to_file=True,
        file_path=PATH,
    )
    logger.info(f"Relationships for CUI 'C0011849':\n{cui_definition}")
    sys.stdout.flush()
