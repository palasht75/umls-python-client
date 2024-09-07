import requests
import logging
from relationship_labels import RELATION_LABELS
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

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
            logger.error(f"API request failed with status code {response.status_code}: {response.text}")
            return {"error": f"API request failed with status code {response.status_code}: {response.text}"}


class SourceAPI(UMLSAPIBase):
    """Class for handling source-asserted UMLS API requests."""

    def get_source_concept(self, source, id):
        """Retrieve information about a known source concept or descriptor."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching source concept: {source}/{id}")
        return self._handle_response(response)

    def get_source_atoms(self, source, id):
        """Retrieve atoms for a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/atoms"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching source atoms: {source}/{id}")
        return self._handle_response(response)
    
    def get_source_parents(self, source, id):
        """Retrieve immediate parents of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/parents"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_source_children(self, source, id):
        """Retrieve immediate children of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/children"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_source_ancestors(self, source, id):
        """Retrieve all ancestors of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/ancestors"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching ancestors for: {source}/{id}")
        return self._handle_response(response)

    def get_source_descendants(self, source, id):
        """Retrieve all descendants of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/descendants"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching descendants for: {source}/{id}")
        return self._handle_response(response)
    
    
    def get_source_attributes(self, source, id):
        """Retrieve information about source-asserted attributes."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/attributes"
        params = {'apiKey': self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)
    

    def get_concept_pathways(self, source, id):
        """Retrieve full parent-child pathways from the root to the concept and its descendants."""
        def fetch_pathways_recursive(concept_id, pathways, depth=0):
            """Fetch pathways for a concept recursively."""
            if depth > 10:  # Limiting recursion depth
                logger.info(f"Reached maximum depth for concept: {concept_id}")
                return
            parents_response = self.get_source_parents(source, concept_id)
            children_response = self.get_source_children(source, concept_id)
            parents = parents_response.get('result', [])
            children = children_response.get('result', [])
            if parents:
                pathways.setdefault(f"level_{depth}_parents", []).extend([parent.get('name') for parent in parents])
                for parent in parents:
                    fetch_pathways_recursive(parent.get('ui'), pathways, depth + 1)
            if children:
                pathways.setdefault(f"level_{depth}_children", []).extend([child.get('name') for child in children])
                for child in children:
                    fetch_pathways_recursive(child.get('ui'), pathways, depth + 1)
        pathways = {}
        fetch_pathways_recursive(id, pathways)
        return pathways

    def get_concepts_by_relation(self, source, id, relation_type):
        """Retrieve related concepts based on the specified relationship type."""
        relations = self.get_source_concept(source, id).get("result", {}).get("relations", [])
        related_concepts = {relation_type: [relation.get("relatedConcept", {}).get("name") for relation in relations if relation.get("relationLabel").lower() == relation_type.lower()]}
        return related_concepts

    def get_concept_attributes(self, source, id):
        """Retrieve specific attributes of a source-asserted concept."""
        attributes_response = self.get_source_attributes(source, id)
        attributes = attributes_response.get('result', [])
        attribute_dict = {attribute.get('name'): attribute.get('value') for attribute in attributes if attribute.get('name') and attribute.get('value')}
        return attribute_dict

    def compare_concepts(self, source, id1, id2):
        """Compare two concepts by examining their relationships, ancestors, and descendants."""
        concept_1_ancestors = self.get_source_ancestors(source, id1).get('result', [])
        concept_2_ancestors = self.get_source_ancestors(source, id2).get('result', [])
        concept_1_descendants = self.get_source_descendants(source, id1).get('result', [])
        concept_2_descendants = self.get_source_descendants(source, id2).get('result', [])
        comparison = {
            "concept_1": id1,
            "concept_2": id2,
            "shared_ancestors": [ancestor.get('name') for ancestor in concept_1_ancestors if ancestor in concept_2_ancestors],
            "shared_descendants": [descendant.get('name') for descendant in concept_1_descendants if descendant in concept_2_descendants],
            "unique_to_concept_1": {
                "ancestors": [ancestor.get('name') for ancestor in concept_1_ancestors if ancestor not in concept_2_ancestors],
                "descendants": [descendant.get('name') for descendant in concept_1_descendants if descendant not in concept_2_descendants]
            },
            "unique_to_concept_2": {
                "ancestors": [ancestor.get('name') for ancestor in concept_2_ancestors if ancestor not in concept_1_ancestors],
                "descendants": [descendant.get('name') for descendant in concept_2_descendants if descendant not in concept_1_descendants]
            }
        }
        return comparison

    def get_concept_coverage(self, source, id):
        """Check in which medical systems the concept is present."""
        concept_response = self.get_source_concept(source, id)
        source_systems = concept_response.get('result', {}).get('rootSource', [])
        return {"concept_id": id, "covered_in_sources": source_systems}

    def aggregate_children_by_attribute(self, source, id, attribute_name):
        """Aggregate children of a concept based on a specific attribute."""
        children_response = self.get_source_children(source, id)
        children = children_response.get('result', [])
        attribute_aggregation = {}
        for child in children:
            child_id = child.get('ui')
            child_attributes = self.get_concept_attributes(source, child_id)
            attribute_value = child_attributes.get(attribute_name, "Unknown")
            attribute_aggregation.setdefault(attribute_value, []).append(child.get('name'))
        return attribute_aggregation

    # New function to get the family tree structure
    def get_family_tree(self, source, id, max_depth=3):
        """Retrieve a family tree structure with relationships organized in a hierarchy of ancestors and descendants."""
        
        def fetch_ancestors(concept_id, hierarchy, depth=0):
            """Recursively fetch ancestors and add them to the family tree."""
            if depth >= max_depth:
                return
            response = self.get_source_parents(source, concept_id)
            parents = response.get('result', [])
            if not parents:
                logger.info(f"No more parents found for: {concept_id}")
                return
            for parent in parents:
                parent_name = parent.get('name')
                parent_id = parent.get('ui')
                if parent_name:
                    hierarchy.setdefault(f"level_{depth}_parents", []).append(parent_name)
                    fetch_ancestors(parent_id, hierarchy, depth + 1)

        def fetch_descendants(concept_id, hierarchy, depth=0):
            """Recursively fetch descendants and add them to the family tree."""
            if depth >= max_depth:
                return
            response = self.get_source_children(source, concept_id)
            children = response.get('result', [])
            if not children:
                logger.info(f"No more children found for: {concept_id}")
                return
            for child in children:
                child_name = child.get('name')
                child_id = child.get('ui')
                if child_name:
                    hierarchy.setdefault(f"level_{depth}_children", []).append(child_name)
                    fetch_descendants(child_id, hierarchy, depth + 1)

        # Initialize family tree structure
        family_tree = {
            "concept_id": id,
            "concept_name": None,
            "ancestors": {},
            "descendants": {}
        }

        # Fetch source concept details to get the name
        source_concept = self.get_source_concept(source, id)
        family_tree["concept_name"] = source_concept.get("result", {}).get("name", "Unknown Concept")

        # Fetch ancestors and descendants in family tree structure
        fetch_ancestors(id, family_tree['ancestors'])
        fetch_descendants(id, family_tree['descendants'])

        return family_tree
    
    def get_source_relations(self, source, id, include_relation_labels=None, include_additional_labels=None, 
                             include_obsolete=False, include_suppressible=False, page_number=1, page_size=25):
        """Retrieve relationships for a known source-asserted identifier with optional parameters."""

        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/relations"
        
        # Parameters based on the provided screenshot
        params = {
            'apiKey': self.api_key,
            'includeRelationLabels': include_relation_labels,
            'includeAdditionalRelationLabels': include_additional_labels,
            'includeObsolete': str(include_obsolete).lower(),
            'includeSuppressible': str(include_suppressible).lower(),
            'pageNumber': page_number,
            'pageSize': page_size
        }

        # Filter out any None values from params
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(url, params=params)
        logger.info(f"Fetching relations for concept: {source}/{id}")
        return self._handle_response(response)

    # Custom recursive method with logging
    def get_full_hierarchy_recursive(self, source, id):
        """Recursively retrieve all ancestors and descendants until root/leaf, with logging."""
        def fetch_ancestors_recursive(concept_id, hierarchy, depth=0):
            """Recursively fetch ancestors."""
            logger.info(f"Fetching ancestors at depth {depth} for concept: {concept_id}")
            response = self.get_source_ancestors(source, concept_id)
            ancestors = response.get('result', [])
            if not ancestors:
                logger.info(f"No more ancestors found for: {concept_id}")
                return
            for ancestor in ancestors:
                ancestor_id = ancestor.get('ui')
                if ancestor_id and ancestor_id not in [a.get('ui') for a in hierarchy['ancestors']]:
                    hierarchy['ancestors'].append(ancestor)
                    fetch_ancestors_recursive(ancestor_id, hierarchy, depth + 1)

        def fetch_descendants_recursive(concept_id, hierarchy, depth=0):
            """Recursively fetch descendants."""
            logger.info(f"Fetching descendants at depth {depth} for concept: {concept_id}")
            response = self.get_source_descendants(source, concept_id)
            descendants = response.get('result', [])
            if not descendants:
                logger.info(f"No more descendants found for: {concept_id}")
                return
            for descendant in descendants:
                descendant_id = descendant.get('ui')
                if descendant_id and descendant_id not in [d.get('ui') for d in hierarchy['descendants']]:
                    hierarchy['descendants'].append(descendant)
                    fetch_descendants_recursive(descendant_id, hierarchy, depth + 1)

        # Initialize hierarchy structure
        hierarchy = {
            "concept_id": id,
            "ancestors": [],
            "descendants": []
        }

        # Recursively fetch ancestors and descendants with logging
        fetch_ancestors_recursive(id, hierarchy)
        fetch_descendants_recursive(id, hierarchy)

        return hierarchy


    def print_available_relations(self):
        """Print available relationship labels."""
        logger.info("Available relation labels:")
        for code, description in RELATION_LABELS.items():
            print(f"{code}: {description}")

# Example usage of SourceAPI with logging
if __name__ == "__main__":
    # Replace with your UMLS API key
    api_key = "cf2c642d-21f2-4f5b-97fe-b271c5f30591"
    source = "SNOMEDCT_US"
    source_id = "9468002"

    source_api = SourceAPI(api_key)
    # Retrieve Source Concept Information
    # print("Source Concept Information:")
    # print(source_api.get_source_concept(source, source_id))

    # # Retrieve Atoms for a Source-Asserted Identifier
    # print("\nAtoms Information:")
    # print(source_api.get_source_atoms(source, source_id))

    # # Retrieve Immediate Parents for a Source-Asserted Identifier
    # print("\nParents Information:")
    # print(source_api.get_source_parents(source, source_id))

    # # Retrieve Immediate Children for a Source-Asserted Identifier
    # print("\nChildren Information:")
    # print(source_api.get_source_children(source, source_id))

    # # Retrieve Ancestors for a Source-Asserted Identifier
    # print("\nAncestors Information:")
    # print(source_api.get_source_ancestors(source, source_id))

    # # Retrieve Descendants for a Source-Asserted Identifier
    # print("\nDescendants Information:")
    # print(source_api.get_source_descendants(source, source_id))

    # # Retrieve Attributes for a Source-Asserted Identifier
    # print("\nAttributes Information:")
    # print(source_api.get_source_attributes(source, source_id))

    # # Retrieve Full Hierarchy Recursively with logging enabled
    # logger.info("\nFull Recursive Hierarchy Fetching Started:")
    # full_hierarchy = source_api.get_full_hierarchy_recursive(source, source_id)
    # logger.info("\nFull Recursive Hierarchy Fetching Complete:")
    # logger.info(full_hierarchy)


    # # Retrieve the family tree structure with max_depth of 3
    # logger.info("\nFetching Family Tree:")
    # family_tree = source_api.get_family_tree(source, source_id, max_depth=3)
    # logger.info("\nFamily Tree Fetch Complete:")
    # logger.info(family_tree)


       # Get concept pathways
    # logger.info("Fetching concept pathways:")
    # pathways = source_api.get_concept_pathways(source, source_id)
    # logger.info(f"Pathways: {pathways}")

    # # Get concepts by relation type
    # logger.info("Fetching concepts by relation:")
    # related_concepts = source_api.get_concepts_by_relation(source, source_id, 'broader')
    # logger.info(f"Related Concepts: {related_concepts}")

    # Get concept attributes
    # logger.info("Fetching concept attributes:")
    # attributes = source_api.get_concept_attributes(source, source_id)
    # logger.info(f"Attributes: {attributes}")

    # # Compare two concepts
    # logger.info("Comparing two concepts:")
    # comparison = source_api.compare_concepts(source, source_id, '9468003')  # Example other concept ID
    # logger.info(f"Comparison: {comparison}")

    # # Get concept coverage across medical systems
    # logger.info("Fetching concept coverage:")
    # coverage = source_api.get_concept_coverage(source, source_id)
    # logger.info(f"Coverage: {coverage}")

    # # Aggregate children by attribute
    # logger.info("Aggregating children by attribute:")
    # aggregated_children = source_api.aggregate_children_by_attribute(source, source_id, 'attribute_name_here')
    # logger.info(f"Aggregated Children: {aggregated_children}")
        # Get source relations with custom parameters

    logger.info("Printing available relation labels:")
    source_api.print_available_relations()

    logger.info("Fetching source relations:")
    relations = source_api.get_source_relations(source, source_id, include_relation_labels=None, 
                                                include_obsolete=False, include_suppressible=False, page_number=1, page_size=10)
    logger.info(f"Source Relations: {relations}")


    """{
    "concept_id": "9468002",
    "concept_name": "Closed fracture of carpal bone",
    "ancestors": {
        "level_0_parents": ["Fracture of wrist"],
        "level_1_parents": ["Injury of forearm"],
        "level_2_parents": ["Injury of upper limb"]
    },
    "descendants": {
        "level_0_children": ["Closed fracture of scaphoid bone"],
        "level_1_children": ["Fracture of right carpal bone"]
    }
}"""





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
#             return {"error": f"API request failed with status code {response.status_code}: {response.text}"}


# class SourceAPI(UMLSAPIBase):
#     """Class for handling source-asserted UMLS API requests."""

#     def get_source_concept(self, source, id):
#         """Retrieve information about a known source concept or descriptor."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     def get_source_atoms(self, source, id):
#         """Retrieve atoms for a known source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/atoms"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
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

#     def get_source_ancestors(self, source, id):
#         """Retrieve all ancestors of a known source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/ancestors"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     def get_source_descendants(self, source, id):
#         """Retrieve all descendants of a known source-asserted identifier."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/descendants"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)

#     def get_source_attributes(self, source, id):
#         """Retrieve information about source-asserted attributes."""
#         url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/attributes"
#         params = {'apiKey': self.api_key}
#         response = requests.get(url, params=params)
#         return self._handle_response(response)


# # Example usage of SourceAPI
# if __name__ == "__main__":
#     # Replace with your UMLS API key
#     api_key = "YOUR_API_KEY"
#     source = "SNOMEDCT_US"
#     source_id = "9468002"

#     source_api = SourceAPI(api_key)

#     # Retrieve Source Concept Information
#     print("Source Concept Information:")
#     print(source_api.get_source_concept(source, source_id))

#     # Retrieve Atoms for a Source-Asserted Identifier
#     print("\nAtoms Information:")
#     print(source_api.get_source_atoms(source, source_id))

#     # Retrieve Immediate Parents for a Source-Asserted Identifier
#     print("\nParents Information:")
#     print(source_api.get_source_parents(source, source_id))

#     # Retrieve Immediate Children for a Source-Asserted Identifier
#     print("\nChildren Information:")
#     print(source_api.get_source_children(source, source_id))

#     # Retrieve Ancestors for a Source-Asserted Identifier
#     print("\nAncestors Information:")
#     print(source_api.get_source_ancestors(source, source_id))

#     # Retrieve Descendants for a Source-Asserted Identifier
#     print("\nDescendants Information:")
#     print(source_api.get_source_descendants(source, source_id))

#     # Retrieve Attributes for a Source-Asserted Identifier
#     print("\nAttributes Information:")
#     print(source_api.get_source_attributes(source, source_id))

