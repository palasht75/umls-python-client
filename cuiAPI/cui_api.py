import logging
import os

import requests

from baseAPI.umls_api_base import UMLSAPIBase

API_KEY = os.getenv("API_KEY")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class CUIAPI(UMLSAPIBase):
    """
    The CUIAPI class is designed to interact with the UMLS REST API for Concept Unique Identifier (CUI) data retrieval.
    This class provides methods to fetch detailed information, atoms, definitions, and relations related to a given CUI.

    The CUIAPI class allows you to:
    - Retrieve detailed information about a CUI from the UMLS Metathesaurus.
    - Retrieve atoms (the smallest units of meaning) associated with a CUI.
    - Retrieve definitions tied to a given CUI.
    - Retrieve relationships (semantic relations between concepts) for a CUI.

    Attributes:
        api_key (str): The UMLS API key used for authentication (inherited from the UMLSAPIBase class).
        version (str): The version of the UMLS release to use (inherited from UMLSAPIBase).
        base_url (str): The base URL for UMLS API requests (inherited from UMLSAPIBase).
    """

    def get_cui_info(self, cui):
        """
        Fetches detailed information about the specified CUI from the UMLS Metathesaurus.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing the detailed information about the CUI.
        """

        url = f"{self.base_url}/content/{self.version}/CUI/{cui}"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching CUI concept: {cui}")
        return self._handle_response(response)

    def get_atoms(self, cui):
        """
        Fetches atoms associated with the specified CUI.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing atoms related to the CUI.
        """

        url = f"{self.base_url}/content/{self.version}/CUI/{cui}/atoms"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching CUI atoms for: {cui}")
        return self._handle_response(response)

    def get_definitions(self, cui):
        """
        Fetches definitions associated with the specified CUI.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing definitions tied to the CUI.
        """

        url = f"{self.base_url}/content/{self.version}/CUI/{cui}/definitions"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching CUI definitions for: {cui}")
        return self._handle_response(response)

    def get_relations(self, cui):
        # """Retrieve relationships for a given CUI."""

        """
        Fetches relationships for the specified CUI.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing the relationships of the CUI.
        """

        url = f"{self.base_url}/content/{self.version}/CUI/{cui}/relations"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching CUI relations for: {cui}")
        return self._handle_response(response)


# class SourceAPI(UMLSAPIBase):
#     """Class for handling source-asserted UMLS API requests."""

#     def get_source_info(self, source, id):
#         """Retrieve information about a known source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     def get_source_atoms(self, source, id):
#         """Retrieve atoms for a source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/atoms"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     # Add more source-related API functions here as needed.


# class SemanticNetworkAPI(UMLSAPIBase):
#     """Class for handling semantic network UMLS API requests."""

#     def get_semantic_type(self, tui):
#         """Retrieve information for a known Semantic Type identifier (TUI)."""
#         url = f"{self.base_url}/semantic-network/{self.version}/TUI/{tui}"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)


# class CrosswalkAPI(UMLSAPIBase):
#     """Class for handling crosswalk UMLS API requests."""

#     def get_crosswalk(self, source, id):
#         """Retrieve all source-asserted identifiers that share a UMLS CUI."""
#         url = f"{self.base_url}/crosswalk/{self.version}/source/{source}/{id}"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)


# Main program to demonstrate usage of the refactored classes
if __name__ == "__main__":
    # Replace with your UMLS API key
    api_key = API_KEY
    cui = "C0009044"  # Example CUI
    source = "SNOMEDCT_US"
    source_id = "9468002"

    # Example usage for CUI-based API
    cui_api = CUIAPI(api_key)
    print("CUI Information:")
    print(cui_api.get_cui_info(cui))

    print("\nAtoms Information:")
    print(cui_api.get_atoms(cui))

    print("\nDefinitions Information:")
    print(cui_api.get_definitions(cui))

    print("\nRelations Information:")
    print(cui_api.get_relations(cui))

    # # Example usage for Source-based API
    # source_api = SourceAPI(api_key)
    # print("\nSource Information:")
    # print(source_api.get_source_info(source, source_id))

    # print("\nSource Atoms Information:")
    # print(source_api.get_source_atoms(source, source_id))

    # # Example usage for Semantic Network API
    # semantic_api = SemanticNetworkAPI(api_key)
    # print("\nSemantic Type Information:")
    # print(semantic_api.get_semantic_type("T037"))

    # # Example usage for Crosswalk API
    # crosswalk_api = CrosswalkAPI(api_key)
    # print("\nCrosswalk Information:")
    # print(crosswalk_api.get_crosswalk(source, source_id))
