import requests
import logging
from sourceAPI.relationship_labels import RELATION_LABELS
from baseAPI.umls_api_base import UMLSAPIBase

import os

# print("Api-key --> ", os.getenv("API_KEY"))
API_KEY = os.getenv("API_KEY")

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger()


class SourceAPI(UMLSAPIBase):
    """Class for handling source-asserted UMLS API requests."""

    def get_source_concept(self, source :str, id: str):
        """Retrieve information about a known source concept or descriptor."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching source concept: {source}/{id}")
        return self._handle_response(response)

    def get_source_atoms(
        self,
        source,
        id,
        sabs=None,
        ttys=None,
        language=None,
        include_obsolete=False,
        include_suppressible=False,
        page_number=1,
        page_size=25,
    ):
        """Retrieve atoms for a known source-asserted identifier with optional filters."""

        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/atoms"

        # Parameters for the query
        params = {
            "apiKey": self.api_key,
            "sabs": sabs,  # Comma-separated list of source vocabularies (e.g., "SNOMEDCT_US,ICD10CM")
            "ttys": ttys,  # Comma-separated list of term types (e.g., "PT,SY")
            "language": language,  # Specific language (e.g., "ENG", "SPA")
            "includeObsolete": str(
                include_obsolete
            ).lower(),  # Include obsolete atoms or not
            "includeSuppressible": str(
                include_suppressible
            ).lower(),  # Include suppressible atoms or not
            "pageNumber": page_number,  # Page number to fetch
            "pageSize": page_size,  # Number of results per page
        }

        # Filter out any None values from the parameters (as they are optional)
        params = {k: v for k, v in params.items() if v is not None}

        # Make the request
        response = requests.get(url, params=params)
        logger.info(f"Fetching source atoms for: {source}/{id}")
        return self._handle_response(response)

    def get_source_parents(self, source, id):
        """Retrieve immediate parents of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/parents"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_source_children(self, source, id):
        """Retrieve immediate children of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/children"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_source_ancestors(self, source, id):
        """Retrieve all ancestors of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/ancestors"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching ancestors for: {source}/{id}")
        return self._handle_response(response)

    def get_source_descendants(self, source, id):
        """Retrieve all descendants of a known source-asserted identifier."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/descendants"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        logger.info(f"Fetching descendants for: {source}/{id}")
        return self._handle_response(response)

    def get_source_attributes(self, source, id):
        """Retrieve information about source-asserted attributes."""
        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/attributes"
        params = {"apiKey": self.api_key}
        response = requests.get(url, params=params)
        return self._handle_response(response)

    def get_concept_pathways(self, source, id, max_depth=2):
        """
        Retrieve full parent-child pathways from the root to the concept and its descendants iteratively.

        Parameters:
            - source: The source vocabulary (e.g., SNOMEDCT_US, LOINC)
            - id: The concept ID for which to fetch the pathways
            - max_depth: The maximum depth to explore (default is 2)
        """

        def fetch_parents_children(concept_id, pathways, cache):
            """Fetch parents and children for a concept and store them in cache."""
            # Check if we have already fetched this concept
            if concept_id in cache:
                return cache[concept_id]

            # Fetch parents and children using the source API methods
            parents_response = self.get_source_parents(source, concept_id)
            children_response = self.get_source_children(source, concept_id)
            parents = parents_response.get("result", [])
            children = children_response.get("result", [])

            # Cache the results to avoid redundant API calls
            cache[concept_id] = {"parents": parents, "children": children}
            logger.info(f"Cache updated: {cache}")

            # Add to pathways
            if parents:
                pathways.setdefault(f"concept_{concept_id}_parents", []).extend(
                    [parent.get("name") for parent in parents]
                )
            if children:
                pathways.setdefault(f"concept_{concept_id}_children", []).extend(
                    [child.get("name") for child in children]
                )

            return cache[concept_id]

        # Initialize structures
        cache = {}
        pathways = {}
        queue = [(id, 0)]  # (concept_id, depth)

        # Process concepts iteratively using a queue (Breadth-First Search)
        while queue:
            concept_id, depth = queue.pop(0)  # Dequeue the first element

            if depth > max_depth:
                logger.info(f"Reached maximum depth for concept: {concept_id}")
                continue

            # Fetch the parents and children
            concept_data = fetch_parents_children(concept_id, pathways, cache)
            parents = concept_data["parents"]
            children = concept_data["children"]

            # Enqueue parents and children for further exploration
            for parent in parents:
                queue.append((parent.get("ui"), depth + 1))
            for child in children:
                queue.append((child.get("ui"), depth + 1))

        return pathways

    def get_relations(self, relations_url):
        """Make a second request to the relations endpoint and retrieve related concepts."""
        params = {"apiKey": self.api_key}
        response = requests.get(relations_url, params=params)
        logger.info(f"Fetching relations from URL: {relations_url}")
        return self._handle_response(response)

    def get_related_concepts_by_relation_type(self, source, id, relation_type):
        """Retrieve related concepts based on the specified relationship type."""
        # Step 1: Fetch the source concept
        concept_response = self.get_source_concept(source, id)

        # Step 2: Check if 'relations' is an endpoint URL
        relations_url = concept_response.get("result", {}).get("relations", "")
        if isinstance(relations_url, str) and relations_url.startswith("http"):
            # If it's a URL, make a second request to fetch relations
            relations_response = self.get_relations(relations_url)
            relations = relations_response.get("result", [])
        else:
            logger.warning(f"No valid relations endpoint found for concept: {id}")
            return {relation_type: []}

        # Step 3: Filter relations based on the specified relationship type
        related_concepts = []
        for relation in relations:
            # Ensure that the relation is a dictionary and has the required fields
            if (
                isinstance(relation, dict)
                and relation.get("relationLabel", "").lower() == relation_type.lower()
            ):
                # Use 'relatedIdName' to extract the related concept's name
                related_concept_name = relation.get("relatedIdName", "Unknown Concept")
                related_concepts.append(related_concept_name)

        # Step 4: Return related concepts based on the relation type
        if not related_concepts:
            logger.warning(
                f"No related concepts found for relation type '{relation_type}' in concept: {id}"
            )
        else:
            logger.info(
                f"Found {len(related_concepts)} related concepts for relation type '{relation_type}'."
            )

        return {relation_type: related_concepts}

    def get_concept_attributes(self, source, id):
        """Retrieve specific attributes of a source-asserted concept."""
        attributes_response = self.get_source_attributes(source, id)
        attributes = attributes_response.get("result", [])
        attribute_dict = {
            attribute.get("name"): attribute.get("value")
            for attribute in attributes
            if attribute.get("name") and attribute.get("value")
        }
        return attribute_dict

    def compare_concepts(self, source, id1, id2):
        """Compare two concepts by examining their relationships, ancestors, and descendants."""
        concept_1_ancestors = self.get_source_ancestors(source, id1).get("result", [])
        concept_2_ancestors = self.get_source_ancestors(source, id2).get("result", [])
        concept_1_descendants = self.get_source_descendants(source, id1).get(
            "result", []
        )
        concept_2_descendants = self.get_source_descendants(source, id2).get(
            "result", []
        )
        comparison = {
            "concept_1": id1,
            "concept_2": id2,
            "shared_ancestors": [
                ancestor.get("name")
                for ancestor in concept_1_ancestors
                if ancestor in concept_2_ancestors
            ],
            "shared_descendants": [
                descendant.get("name")
                for descendant in concept_1_descendants
                if descendant in concept_2_descendants
            ],
            "unique_to_concept_1": {
                "ancestors": [
                    ancestor.get("name")
                    for ancestor in concept_1_ancestors
                    if ancestor not in concept_2_ancestors
                ],
                "descendants": [
                    descendant.get("name")
                    for descendant in concept_1_descendants
                    if descendant not in concept_2_descendants
                ],
            },
            "unique_to_concept_2": {
                "ancestors": [
                    ancestor.get("name")
                    for ancestor in concept_2_ancestors
                    if ancestor not in concept_1_ancestors
                ],
                "descendants": [
                    descendant.get("name")
                    for descendant in concept_2_descendants
                    if descendant not in concept_1_descendants
                ],
            },
        }
        return comparison

    def get_concept_coverage(self, source, id):
        """Check in which medical systems the concept is present."""
        concept_response = self.get_source_concept(source, id)
        source_systems = concept_response.get("result", {}).get("rootSource", [])
        return {"concept_id": id, "covered_in_sources": source_systems}

    def aggregate_children_by_attribute(self, source, id, attribute_name):
        """Aggregate children of a concept based on a specific attribute."""
        children_response = self.get_source_children(source, id)
        children = children_response.get("result", [])
        attribute_aggregation = {}
        for child in children:
            child_id = child.get("ui")
            child_attributes = self.get_concept_attributes(source, child_id)
            attribute_value = child_attributes.get(attribute_name, "Unknown")
            attribute_aggregation.setdefault(attribute_value, []).append(
                child.get("name")
            )
        return attribute_aggregation

    # New function to get the family tree structure
    def get_family_tree(self, source, id, max_depth=3):
        """Retrieve a family tree structure with relationships organized in a hierarchy of ancestors and descendants."""

        def fetch_ancestors(concept_id, hierarchy, depth=0):
            """Recursively fetch ancestors and add them to the family tree."""
            if depth >= max_depth:
                return
            response = self.get_source_parents(source, concept_id)
            parents = response.get("result", [])
            if not parents:
                logger.info(f"No more parents found for: {concept_id}")
                return
            for parent in parents:
                parent_name = parent.get("name")
                parent_id = parent.get("ui")
                if parent_name:
                    hierarchy.setdefault(f"level_{depth}_parents", []).append(
                        parent_name
                    )
                    fetch_ancestors(parent_id, hierarchy, depth + 1)

        def fetch_descendants(concept_id, hierarchy, depth=0):
            """Recursively fetch descendants and add them to the family tree."""
            if depth >= max_depth:
                return
            response = self.get_source_children(source, concept_id)
            children = response.get("result", [])
            if not children:
                logger.info(f"No more children found for: {concept_id}")
                return
            for child in children:
                child_name = child.get("name")
                child_id = child.get("ui")
                if child_name:
                    hierarchy.setdefault(f"level_{depth}_children", []).append(
                        child_name
                    )
                    fetch_descendants(child_id, hierarchy, depth + 1)

        # Initialize family tree structure
        family_tree = {
            "concept_id": id,
            "concept_name": None,
            "ancestors": {},
            "descendants": {},
        }

        # Fetch source concept details to get the name
        source_concept = self.get_source_concept(source, id)
        family_tree["concept_name"] = source_concept.get("result", {}).get(
            "name", "Unknown Concept"
        )

        # Fetch ancestors and descendants in family tree structure
        fetch_ancestors(id, family_tree["ancestors"])
        fetch_descendants(id, family_tree["descendants"])

        return family_tree

    def get_source_relations(
        self,
        source,
        id,
        include_relation_labels=None,
        include_additional_labels=None,
        include_obsolete=False,
        include_suppressible=False,
        page_number=1,
        page_size=25,
    ):
        """Retrieve relationships for a known source-asserted identifier with optional parameters."""

        url = f"{self.base_url}/content/{self.version}/source/{source}/{id}/relations"

        # Parameters based on the provided screenshot
        params = {
            "apiKey": self.api_key,
            "includeRelationLabels": include_relation_labels,
            "includeAdditionalRelationLabels": include_additional_labels,
            "includeObsolete": str(include_obsolete).lower(),
            "includeSuppressible": str(include_suppressible).lower(),
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        # Filter out any None values from params
        params = {k: v for k, v in params.items() if v is not None}

        response = requests.get(url, params=params)
        logger.info(f"Fetching relations for concept: {source}/{id}")
        return self._handle_response(response)

    # Custom recursive method with logging
    def get_full_hierarchy_recursive(self, source, id, depth=0):
        """Recursively retrieve all ancestors and descendants until root/leaf, with logging."""

        def fetch_ancestors_recursive(concept_id, hierarchy, depth=0):
            """Recursively fetch ancestors."""
            logger.info(
                f"Fetching ancestors at depth {depth} for concept: {concept_id}"
            )
            response = self.get_source_ancestors(source, concept_id)
            ancestors = response.get("result", [])
            if not ancestors:
                logger.info(f"No more ancestors found for: {concept_id}")
                return
            for ancestor in ancestors:
                ancestor_id = ancestor.get("ui")
                if ancestor_id and ancestor_id not in [
                    a.get("ui") for a in hierarchy["ancestors"]
                ]:
                    hierarchy["ancestors"].append(ancestor)
                    fetch_ancestors_recursive(ancestor_id, hierarchy, depth + 1)

        def fetch_descendants_recursive(concept_id, hierarchy, depth=0):
            """Recursively fetch descendants."""
            logger.info(
                f"Fetching descendants at depth {depth} for concept: {concept_id}"
            )
            response = self.get_source_descendants(source, concept_id)
            descendants = response.get("result", [])
            if not descendants:
                logger.info(f"No more descendants found for: {concept_id}")
                return
            for descendant in descendants:
                descendant_id = descendant.get("ui")
                if descendant_id and descendant_id not in [
                    d.get("ui") for d in hierarchy["descendants"]
                ]:
                    hierarchy["descendants"].append(descendant)
                    fetch_descendants_recursive(descendant_id, hierarchy, depth + 1)

        # Initialize hierarchy structure
        hierarchy = {"concept_id": id, "ancestors": [], "descendants": []}

        # Recursively fetch ancestors and descendants with logging
        fetch_ancestors_recursive(id, hierarchy, depth=depth)
        fetch_descendants_recursive(id, hierarchy, depth=depth)

        return hierarchy

    def print_available_relations(self):
        """Print available relationship labels."""
        logger.info("Available relation labels:")
        for code, description in RELATION_LABELS.items():
            print(f"{code}: {description}")


