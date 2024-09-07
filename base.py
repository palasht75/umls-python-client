import requests

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
            return {"error": f"API request failed with status code {response.status_code}: {response.text}"}


class CUIAPI(UMLSAPIBase):
    """Class for handling CUI-based UMLS API requests."""

    def get_cui_info(self, cui):
        """Retrieve CUI information."""
        url = f"{self.base_url}/content/{self.version}/CUI/{cui}"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_atoms(self, cui):
        """Retrieve atoms for a given CUI."""
        url = f"{self.base_url}/content/{self.version}/CUI/{cui}/atoms"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_definitions(self, cui):
        """Retrieve definitions for a given CUI."""
        url = f"{self.base_url}/content/{self.version}/CUI/{cui}/definitions"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_relations(self, cui):
        """Retrieve relationships for a given CUI."""
        url = f"{self.base_url}/content/{self.version}/CUI/{cui}/relations"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)


class SourceAPI(UMLSAPIBase):
    """Class for handling source-asserted UMLS API requests."""

    def get_source_info(self, source, id):
        """Retrieve information about a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_source_atoms(self, source, id):
        """Retrieve atoms for a source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/atoms"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    # Add more source-related API functions here as needed.


class SemanticNetworkAPI(UMLSAPIBase):
    """Class for handling semantic network UMLS API requests."""

    def get_semantic_type(self, tui):
        """Retrieve information for a known Semantic Type identifier (TUI)."""
        url = f"{self.base_url}/semantic-network/{self.version}/TUI/{tui}"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)


class CrosswalkAPI(UMLSAPIBase):
    """Class for handling crosswalk UMLS API requests."""

    def get_crosswalk(self, source, id):
        """Retrieve all source-asserted identifiers that share a UMLS CUI."""
        url = f"{self.base_url}/crosswalk/{self.version}/source/{source}/{id}"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)


# Main program to demonstrate usage of the refactored classes
if __name__ == "__main__":
    # Replace with your UMLS API key
    api_key = "cf2c642d-21f2-4f5b-97fe-b271c5f30591"
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

    # Example usage for Source-based API
    source_api = SourceAPI(api_key)
    print("\nSource Information:")
    print(source_api.get_source_info(source, source_id))

    print("\nSource Atoms Information:")
    print(source_api.get_source_atoms(source, source_id))

    # Example usage for Semantic Network API
    semantic_api = SemanticNetworkAPI(api_key)
    print("\nSemantic Type Information:")
    print(semantic_api.get_semantic_type("T037"))

    # Example usage for Crosswalk API
    crosswalk_api = CrosswalkAPI(api_key)
    print("\nCrosswalk Information:")
    print(crosswalk_api.get_crosswalk(source, source_id))
