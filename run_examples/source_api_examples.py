import os
import logging
from sourceAPI.source_api import SourceAPI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Fetch the API key from environment variables
API_KEY = os.getenv("API_KEY")

# Main function to demonstrate various functionalities of the SourceAPI
if __name__ == "__main__":
    # Initialize your UMLS API key from environment or configuration
    api_key = API_KEY
    if not api_key:
        logger.error("API Key is missing. Please set it in your environment.")
        exit(1)
    
    # Specify the source (e.g., SNOMEDCT_US) and a concept ID
    source = "SNOMEDCT_US"
    source_id = "9468002"  # Example concept ID

    # Initialize the SourceAPI class with your API key
    source_api = SourceAPI(api_key)

    #############################
    # Retrieve Source Concept Information
    #############################
    logger.info("Retrieving source concept information for the specified source and ID:")
    concept_info = source_api.get_source_concept(source, source_id)
    logger.info(f"Source Concept Information: {concept_info}")

    #############################
    # Retrieve Atoms for a Source-Asserted Identifier
    #############################
    logger.info("Fetching atoms for the source-asserted identifier with various filters:")
    atoms = source_api.get_source_atoms(
        source, source_id, sabs="SNOMEDCT_US", ttys="PT", language="ENG", 
        include_obsolete=True, include_suppressible=False, page_number=1, page_size=10
    )
    logger.info(f"Atoms Information: {atoms}")

    #############################
    # Retrieve Immediate Parents for a Source-Asserted Identifier
    #############################
    logger.info("Fetching immediate parent concepts for the specified source and ID:")
    parents = source_api.get_source_parents(source, source_id)
    logger.info(f"Parents Information: {parents}")

    #############################
    # Retrieve Immediate Children for a Source-Asserted Identifier
    #############################
    logger.info("Fetching immediate child concepts for the specified source and ID:")
    children = source_api.get_source_children(source, source_id)
    logger.info(f"Children Information: {children}")

    #############################
    # Retrieve Ancestors for a Source-Asserted Identifier
    #############################
    logger.info("Fetching ancestors for the specified source and ID:")
    ancestors = source_api.get_source_ancestors(source, source_id)
    logger.info(f"Ancestors Information: {ancestors}")

    #############################
    # Retrieve Descendants for a Source-Asserted Identifier
    #############################
    logger.info("Fetching descendants for the specified source and ID:")
    descendants = source_api.get_source_descendants(source, source_id)
    logger.info(f"Descendants Information: {descendants}")

    #############################
    # Retrieve Attributes for a Source-Asserted Identifier
    #############################
    logger.info("Fetching attributes for the specified source and ID:")
    attributes = source_api.get_source_attributes(source, source_id)
    logger.info(f"Attributes Information: {attributes}")

    #############################
    # Retrieve Full Hierarchy Recursively
    #############################
    logger.info("Recursively fetching the full hierarchy for the concept (parents and children):")
    full_hierarchy = source_api.get_full_hierarchy_recursive(source, source_id, depth=0)
    logger.info(f"Full Recursive Hierarchy: {full_hierarchy}")

    #############################
    # Retrieve Family Tree (Parent-Child Relationships)
    #############################
    logger.info("Fetching family tree (parents and children) with a maximum depth of 3:")
    family_tree = source_api.get_family_tree(source, source_id, max_depth=3)
    logger.info(f"Family Tree: {family_tree}")

    #############################
    # Fetch Concept Pathways (Parent-Child Pathways)
    #############################
    logger.info("Fetching parent-child pathways for the concept with a specified depth:")
    pathways = source_api.get_concept_pathways(source, source_id, max_depth=0)
    logger.info(f"Concept Pathways: {pathways}")

    #############################
    # Fetch Related Concepts Based on Relationship Type (e.g., 'RB' for broader)
    #############################
    relation_type = "RB"  # Broader relationship
    logger.info("Fetching related concepts based on the specified relationship type (e.g., broader concepts):")
    related_concepts = source_api.get_related_concepts_by_relation_type(source, source_id, relation_type)
    logger.info(f"Related Concepts (Broader Relationship): {related_concepts}")

    #############################
    # Compare Two Concepts
    #############################
    logger.info("Comparing two concepts for similarity or differences:")
    comparison = source_api.compare_concepts(source, source_id, "9468003")  # Example of another concept ID
    logger.info(f"Comparison between concepts: {comparison}")

    #############################
    # Get Concept Coverage Across Medical Systems
    #############################
    logger.info("Fetching coverage of the concept across multiple medical systems:")
    coverage = source_api.get_concept_coverage(source, source_id)
    logger.info(f"Concept Coverage: {coverage}")

    #############################
    # Aggregate Children by Attribute
    #############################
    logger.info("Aggregating children of the concept by a specific attribute (replace with actual attribute):")
    aggregated_children = source_api.aggregate_children_by_attribute(source, source_id, "attribute_name_here")
    logger.info(f"Aggregated Children by Attribute: {aggregated_children}")

    #############################
    # Fetch Source Relations with Custom Parameters
    #############################
    logger.info("Fetching available source relations for the concept with optional filters:")
    relations = source_api.get_source_relations(
        source, source_id, include_relation_labels=None, include_obsolete=False, 
        include_suppressible=False, page_number=1, page_size=10
    )
    logger.info(f"Source Relations: {relations}")
