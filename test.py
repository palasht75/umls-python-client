# # import requests
# # import logging

# # # Configure logging
# # logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# # logger = logging.getLogger()

# # class UMLSAPIBase:
# #     """Base class for common functionality like request handling."""
    
# #     def __init__(self, api_key, version="current"):
# #         self.api_key = api_key
# #         self.base_url = "https://uts-ws.nlm.nih.gov/rest"
# #         self.version = version

# #     def _handle_response(self, response):
# #         """Handle API responses."""
# #         if response.status_code == 200:
# #             return response.json()
# #         else:
# #             logger.error(f"API request failed with status code {response.status_code}: {response.text}")
# #             return {"error": f"API request failed with status code {response.status_code}: {response.text}"}


# # class SourceAPI(UMLSAPIBase):
# #     """Class for handling source-asserted UMLS API requests."""

# #     def get_source_concept(self, source, id):
# #         """Retrieve information about a known source concept or descriptor."""
# #         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
# #         params = {'apiKey': self.api_key}
# #         response = requests.get(url, params=params)
# #         logger.info(f"Fetching source concept: {source}/{id}")
# #         return self._handle_response(response)

# #     def get_source_ancestors(self, source, id):
# #         """Retrieve all ancestors of a known source-asserted identifier."""
# #         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/ancestors"
# #         params = {'apiKey': self.api_key}
# #         response = requests.get(url, params=params)
# #         logger.info(f"Fetching ancestors for: {source}/{id}")
# #         return self._handle_response(response)

# #     def get_source_descendants(self, source, id):
# #         """Retrieve all descendants of a known source-asserted identifier."""
# #         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/descendants"
# #         params = {'apiKey': self.api_key}
# #         response = requests.get(url, params=params)
# #         logger.info(f"Fetching descendants for: {source}/{id}")
# #         return self._handle_response(response)

# #     # New function to get simplified hierarchy by name
# #     def get_simplified_hierarchy(self, source, id, max_depth=3):
# #         """Retrieve a simplified hierarchy of ancestors and descendants by name."""
        
# #         def fetch_ancestors_recursive(concept_id, hierarchy, depth=0):
# #             """Recursively fetch ancestors by name."""
# #             if depth > max_depth:
# #                 logger.info(f"Reached max recursion depth of {max_depth}")
# #                 return
# #             response = self.get_source_ancestors(source, concept_id)
# #             ancestors = response.get('result', [])
# #             if not ancestors:
# #                 logger.info(f"No more ancestors found for: {concept_id}")
# #                 return
# #             for ancestor in ancestors:
# #                 ancestor_name = ancestor.get('name')
# #                 ancestor_id = ancestor.get('ui')
# #                 if ancestor_name and ancestor_name not in hierarchy['ancestors']:
# #                     hierarchy['ancestors'].append(ancestor_name)
# #                     fetch_ancestors_recursive(ancestor_id, hierarchy, depth + 1)

# #         def fetch_descendants_recursive(concept_id, hierarchy, depth=0):
# #             """Recursively fetch descendants by name."""
# #             if depth > max_depth:
# #                 logger.info(f"Reached max recursion depth of {max_depth}")
# #                 return
# #             response = self.get_source_descendants(source, concept_id)
# #             descendants = response.get('result', [])
# #             if not descendants:
# #                 logger.info(f"No more descendants found for: {concept_id}")
# #                 return
# #             for descendant in descendants:
# #                 descendant_name = descendant.get('name')
# #                 descendant_id = descendant.get('ui')
# #                 if descendant_name and descendant_name not in hierarchy['descendants']:
# #                     hierarchy['descendants'].append(descendant_name)
# #                     fetch_descendants_recursive(descendant_id, hierarchy, depth + 1)

# #         # Initialize hierarchy structure
# #         hierarchy = {
# #             "concept_id": id,
# #             "ancestors": [],
# #             "descendants": []
# #         }

# #         # Recursively fetch ancestors and descendants by name
# #         fetch_ancestors_recursive(id, hierarchy)
# #         fetch_descendants_recursive(id, hierarchy)

# #         return hierarchy


# # # Example usage of SourceAPI with logging
# # if __name__ == "__main__":
# #     # Replace with your UMLS API key
# #     api_key = "cf2c642d-21f2-4f5b-97fe-b271c5f30591"
# #     source = "SNOMEDCT_US"
# #     source_id = "9468002"

# #     source_api = SourceAPI(api_key)
    
# #     # Retrieve simplified hierarchy with names
# #     logger.info("\nFetching Simplified Hierarchy by Names:")
# #     simple_hierarchy = source_api.get_simplified_hierarchy(source, source_id, max_depth=3)
# #     logger.info("\nSimplified Hierarchy Fetch Complete:")
# #     logger.info(simple_hierarchy)


# import requests
# import logging

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger()

# class UMLSAPIBase:
#     """Base class for common functionality like request handling."""
    
#     def __init__(self, api_key, version="current"):
#         self.api_key = api_key
#         self.base_url = "https://uts-ws.nlm.nih.gov/rest"
#         self.version = version

#     def _handle_response(self, response):
#         """Handle API responses."""
#         if response.status_code == 200:
#             return response.json()
#         else:
#             logger.error(f"API request failed with status code {response.status_code}: {response.text}")
#             return {"error": f"API request failed with status code {response.status_code}: {response.text}"}


# class SourceAPI(UMLSAPIBase):
#     """Class for handling source-asserted UMLS API requests."""

#     def get_source_concept(self, source, id):
#         """Retrieve information about a known source concept or descriptor."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         logger.info(f"Fetching source concept: {source}/{id}")
#         return self._handle_response(response)

#     def get_source_parents(self, source, id):
#         """Retrieve immediate parents of a known source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/parents"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     def get_source_children(self, source, id):
#         """Retrieve immediate children of a known source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/children"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     # New function to get the family tree structure
#     def get_family_tree(self, source, id, max_depth=3):
#         """Retrieve a family tree structure with relationships organized in a hierarchy of ancestors and descendants."""
        
#         def fetch_ancestors(concept_id, hierarchy, depth=0):
#             """Recursively fetch ancestors and add them to the family tree."""
#             if depth >= max_depth:
#                 return
#             response = self.get_source_parents(source, concept_id)
#             parents = response.get('result', [])
#             if not parents:
#                 logger.info(f"No more parents found for: {concept_id}")
#                 return
#             for parent in parents:
#                 parent_name = parent.get('name')
#                 parent_id = parent.get('ui')
#                 if parent_name:
#                     hierarchy.setdefault(f"level_{depth}_parents", []).append(parent_name)
#                     fetch_ancestors(parent_id, hierarchy, depth + 1)

#         def fetch_descendants(concept_id, hierarchy, depth=0):
#             """Recursively fetch descendants and add them to the family tree."""
#             if depth >= max_depth:
#                 return
#             response = self.get_source_children(source, concept_id)
#             children = response.get('result', [])
#             if not children:
#                 logger.info(f"No more children found for: {concept_id}")
#                 return
#             for child in children:
#                 child_name = child.get('name')
#                 child_id = child.get('ui')
#                 if child_name:
#                     hierarchy.setdefault(f"level_{depth}_children", []).append(child_name)
#                     fetch_descendants(child_id, hierarchy, depth + 1)

#         # Initialize family tree structure
#         family_tree = {
#             "concept_id": id,
#             "concept_name": None,
#             "ancestors": {},
#             "descendants": {}
#         }

#         # Fetch source concept details to get the name
#         source_concept = self.get_source_concept(source, id)
#         family_tree["concept_name"] = source_concept.get("result", {}).get("name", "Unknown Concept")

#         # Fetch ancestors and descendants in family tree structure
#         fetch_ancestors(id, family_tree['ancestors'])
#         fetch_descendants(id, family_tree['descendants'])

#         return family_tree


# # Example usage of SourceAPI with logging
# if __name__ == "__main__":
#     # Replace with your UMLS API key
#     api_key = "cf2c642d-21f2-4f5b-97fe-b271c5f30591"
#     source = "SNOMEDCT_US"
#     source_id = "9468002"

#     source_api = SourceAPI(api_key)

#     # Retrieve the family tree structure with max_depth of 3
#     logger.info("\nFetching Family Tree:")
#     family_tree = source_api.get_family_tree(source, source_id, max_depth=3)
#     logger.info("\nFamily Tree Fetch Complete:")
#     logger.info(family_tree)


# {
#     "concept_id": "9468002",
#     "concept_name": "Closed fracture of carpal bone",
#     "ancestors": {
#         "level_0_parents": ["Fracture of wrist"],
#         "level_1_parents": ["Injury of forearm"],
#         "level_2_parents": ["Injury of upper limb"]
#     },
#     "descendants": {
#         "level_0_children": ["Closed fracture of scaphoid bone"],
#         "level_1_children": ["Fracture of right carpal bone"]
#     }
# }
