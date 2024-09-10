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

    # Initialize the SearchAPI class with your API key
    search_api = UMLSClient(api_key=api_key).searchAPI  

    #############################
    # Perform a Basic Search
    #############################
    logger.info("Performing a basic search query for the term 'diabetes':")
    search_results = search_api.search(
        search_string="diabetes",  # The term to search for
        input_type=None,  # None implies search for any input type
        include_obsolete=False,  # Don't include obsolete terms
        include_suppressible=False,  # Don't include suppressible terms
        return_id_type="concept",  # Return UMLS Concept Unique Identifiers (CUIs)
        search_type="words",  # Search using word-based matching
        page_number=1,  # Start from the first page
        page_size=10,  # Limit the result to 10 items per page
    )
    logger.info(f"Search Results for 'diabetes': {search_results}")

    #############################
    # Search with Specific Vocabularies
    #############################
    logger.info("Performing a search with specific vocabularies (SNOMEDCT_US):")
    search_results_vocab = search_api.search(
        search_string="hypertension",  # Search for 'hypertension'
        sabs="SNOMEDCT_US",  # Limit the search to SNOMEDCT_US vocabulary
        return_id_type="concept",  # Return CUIs
        page_number=1,  # Start from the first page
        page_size=10,  # Limit to 10 results per page
    )
    logger.info(
        f"Search Results for 'hypertension' in SNOMEDCT_US:\n {search_results_vocab}"
    )

    #############################
    # Perform an Exact Match Search
    #############################
    logger.info(
        "Performing an exact match search for the term 'myocardial infarction':"
    )
    search_results_exact = search_api.search(
        search_string="myocardial infarction",  # Search for the exact term
        search_type="exact",  # Use exact matching
        return_id_type="concept",  # Return CUIs
        page_number=1,  # Start from the first page
        page_size=10,  # Limit to 10 results per page
    )
    logger.info(
        f"Exact Match Search Results for 'myocardial infarction': {search_results_exact}"
    )

    #############################
    # Perform a Partial Search
    #############################
    logger.info("Performing a partial search for the term 'fracture':")
    search_results_partial = search_api.search(
        search_string="fracture",  # Search for 'fracture'
        partial_search=True,  # Enable partial search
        return_id_type="concept",  # Return CUIs
        page_number=1,  # Start from the first page
        page_size=10,  # Limit to 10 results per page
    )
    logger.info(f"Partial Search Results for 'fracture': {search_results_partial}")

    #############################
    # Perform a Search Including Obsolete Terms
    #############################
    logger.info("Performing a search for 'insulin' including obsolete terms:")
    search_results_obsolete = search_api.search(
        search_string="insulin",  # Search for 'insulin'
        include_obsolete=True,  # Include obsolete terms in the search
        return_id_type="concept",  # Return CUIs
        page_number=1,  # Start from the first page
        page_size=10,  # Limit to 10 results per page
        format="rdf",
        save_to_file=True,
        file_path=os.path.join(PATH, "insulin_search.txt")
    )
    logger.info(
        f"Search Results for 'insulin' including obsolete terms: {search_results_obsolete}"
    )
