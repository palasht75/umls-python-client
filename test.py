from umlsclient import UMLSClient
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Fetch the API key from environment variables
API_KEY = os.getenv("API_KEY")

# Initialize the UMLSClient with your UMLS API key
api_key = API_KEY
umls_client = UMLSClient(api_key)

#############################
# Perform a Search using the Search API
#############################
logger.info("Searching for 'diabetes' using UMLS Search API:")
search_results = umls_client.searchAPI.search(search_string="diabetes")
logger.info(f"Search Results for 'diabetes': {search_results}")

#############################
# Retrieve Source Concept Information using the Source API
#############################
logger.info("Fetching source concept information for SNOMEDCT_US concept '9468002':")
source_concept = umls_client.sourceAPI.get_source_concept(source="SNOMEDCT_US", id="9468002")
logger.info(f"Source Concept Information: {source_concept}")

#############################
# Retrieve CUI Details using the CUI API
#############################
logger.info("Fetching CUI details for 'C0004238':")
cui_details = umls_client.cuiAPI.get_cui_info(cui="C0004238")
logger.info(f"CUI Details: {cui_details}")
