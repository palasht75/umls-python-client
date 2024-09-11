import logging
import os
from cuiAPI.cui_api import CUIAPI

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()

# Fetch the API key from environment variables
API_KEY = os.getenv("API_KEY")

# Main function to demonstrate the CUIAPI functionality
if __name__ == "__main__":
    # Initialize your UMLS API key from environment or configuration
    api_key = API_KEY
    if not api_key:
        logger.error("API Key is missing. Please set it in your environment.")
        exit(1)

    # Initialize the CUIAPI class with your API key
    cui_api = CUIAPI(api_key)

    #############################
    # Fetch CUI Information
    #############################
    logger.info("Fetching CUI information for 'C0011849':")
    cui_info = cui_api.get_cui(cui="C0011849")
    logger.info(f"CUI Information:\n{cui_info}")

    #############################
    # Fetch Atoms for a CUI
    #############################
    logger.info("Fetching atoms for CUI 'C0011849':")
    cui_atoms = cui_api.get_cui_atoms(cui="C0011849", sabs="SNOMEDCT_US", ttys="PT")
    logger.info(f"Atoms for CUI 'C0011849':\n{cui_atoms}")

    #############################
    # Retrieve Relationships for a CUI
    #############################
    logger.info("Fetching relationships for CUI 'C0011849':")
    cui_relationships = cui_api.get_cui_relationships(cui="C0011849", sabs="SNOMEDCT_US")
    logger.info(f"Relationships for CUI 'C0011849':\n{cui_relationships}")

    #############################
    # Retrieve Semantic Types for a CUI
    #############################
    logger.info("Fetching semantic types for CUI 'C0011849':")
    semantic_types = cui_api.get_cui_semantic_types(cui="C0011849")
    logger.info(f"Semantic Types for CUI 'C0011849':\n{semantic_types}")

    #############################
    # Retrieve Attributes for a CUI
    #############################
    logger.info("Fetching attributes for CUI 'C0011849':")
    cui_attributes = cui_api.get_cui_attributes(cui="C0011849")
    logger.info(f"Attributes for CUI 'C0011849':\n{cui_attributes}")

    #############################
    # Fetch Parents and Children for a CUI
    #############################
    logger.info("Fetching family tree (parents and children) for CUI 'C0011849':")
    family_tree = cui_api.get_cui_family_tree(cui="C0011849", max_depth=3, return_indented=True)
    logger.info(f"Family Tree for CUI 'C0011849':\n{family_tree}")