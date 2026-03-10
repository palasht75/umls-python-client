import unittest

from umls_python_client import UMLSClient


class TestClientAliases(unittest.TestCase):
    def test_client_exposes_snake_case_and_legacy_aliases(self):
        client = UMLSClient(api_key="test-key")

        self.assertIs(client.search_api, client.searchAPI)
        self.assertIs(client.source_api, client.sourceAPI)
        self.assertIs(client.cui_api, client.cuiAPI)
        self.assertIs(client.semantic_network_api, client.semanticNetworkAPI)
        self.assertIs(client.crosswalk_api, client.crosswalkAPI)


if __name__ == "__main__":
    unittest.main()
