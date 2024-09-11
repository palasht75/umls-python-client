import logging
import os
import sys

# from umls_python_client.sourceAPI.source_api import SourceAPI
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from umls_python_client.umls_client import UMLSClient


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s", force=True
)
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
    source_api = UMLSClient(api_key).sourceAPI

    #############################
    # Retrieve Source Concept Information
    #############################
    logger.info(
        "Retrieving source concept information for the specified source and ID:"
    )
    concept_info = source_api.get_source_concept(
        source, source_id, return_indented=True
    )
    logger.info(f"Source Concept Information:\n {concept_info}")
    sys.stdout.flush()

    #############################
    # Retrieve Atoms for a Source-Asserted Identifier
    #############################
    logger.info(
        "Fetching atoms for the source-asserted identifier with various filters:"
    )
    atoms = source_api.get_source_atoms(
        source,
        source_id,
        sabs="SNOMEDCT_US",
        ttys="PT",
        language="ENG",
        include_obsolete=True,
        include_suppressible=False,
        page_number=1,
        page_size=10,
        format="rdf",
    )
    logger.info(f"Atoms Information: {atoms}")

    #############################
    # Retrieve Immediate Parents for a Source-Asserted Identifier
    #############################
    logger.info("Fetching immediate parent concepts for the specified source and ID:")
    parents = source_api.get_source_parents(source, source_id, format="rdf")
    logger.info(f"Parents Information:\n {parents}")
    sys.stdout.flush()

    #############################
    # Retrieve Immediate Children for a Source-Asserted Identifier
    #############################
    logger.info("Fetching immediate child concepts for the specified source and ID:")
    children = source_api.get_source_children(source, source_id, format="rdf")
    logger.info(f"Children Information:\n {children}")
    sys.stdout.flush()

    #############################
    # Retrieve Ancestors for a Source-Asserted Identifier
    #############################
    logger.info("Fetching ancestors for the specified source and ID:")
    ancestors = source_api.get_source_ancestors(source, source_id)
    logger.info(f"Ancestors Information:\n {ancestors}")
    sys.stdout.flush()

    #############################
    # Retrieve Descendants for a Source-Asserted Identifier
    #############################
    logger.info("Fetching descendants for the specified source and ID:")
    descendants = source_api.get_source_descendants(source, source_id)
    logger.info(f"Descendants Information:\n {descendants}")
    sys.stdout.flush()

    #############################
    # Retrieve Attributes for a Source-Asserted Identifier
    #############################
    logger.info("Fetching attributes for the specified source and ID:")
    attributes = source_api.get_source_attributes(source, source_id)
    logger.info(f"Attributes Information:\n {attributes}")
    sys.stdout.flush()

    #############################
    # Fetch Source Relations with Custom Parameters
    #############################
    logger.info(
        "Fetching available source relations for the concept with optional filters:"
    )
    relations = source_api.get_source_relations(
        source,
        source_id,
        include_relation_labels=None,
        include_obsolete=False,
        include_suppressible=False,
        page_number=1,
        page_size=10,
    )
    logger.info(f"Source Relations:\n {relations}")
    sys.stdout.flush()
    logger.info(f"Source Relations: {relations}")

    # #############################
    # # Retrieve Full Hierarchy Recursively
    # #############################
    # logger.info(
    #     "Recursively fetching the full hierarchy for the concept (parents and children):"
    # )
    # full_hierarchy = source_api.get_full_hierarchy_recursive(source, source_id, depth=1, return_indented=True)
    # logger.info(f"Full Recursive Hierarchy:\n {full_hierarchy} \n")

    #############################
    # Retrieve Family Tree (Parent-Child Relationships)
    #############################
    logger.info(
        "Fetching family tree (parents and children) with a maximum depth of 3:"
    )
    family_tree = source_api.get_family_tree(
        source, source_id, max_depth=3, return_indented=True
    )
    logger.info(f"Family Tree:\n {family_tree}")
    sys.stdout.flush()

    #############################
    # Fetch Concept Pathways (Parent-Child Pathways)
    #############################
    logger.info(
        "Fetching parent-child pathways for the concept with a specified depth:"
    )
    pathways = source_api.get_concept_pathways(
        source, source_id, max_depth=0, return_indented=True
    )
    logger.info(f"Concept Pathways:\n {pathways}")
    sys.stdout.flush()

    #############################
    # Fetch Related Concepts Based on Relationship Type (e.g., 'RB' for broader)
    #############################
    relation_type = "RB"  # Broader relationship
    logger.info(
        "Fetching related concepts based on the specified relationship type (e.g., broader concepts):"
    )
    related_concepts = source_api.get_related_concepts_by_relation_type(
        source, source_id, relation_type, return_indented=True
    )
    logger.info(f"Related Concepts (Broader Relationship):\n {related_concepts}")
    sys.stdout.flush()

    #############################
    # Compare Two Concepts
    #############################
    logger.info("Comparing two concepts for similarity or differences:")
    comparison = source_api.compare_concepts(
        source, id1=source_id, id2="9468003", return_indented=True
    )  # Example of another concept ID
    logger.info(f"Comparison between concepts:\n {comparison}")
    sys.stdout.flush()

    #############################
    # Get Concept Coverage Across Medical Systems
    #############################
    logger.info("Fetching coverage of the concept across multiple medical systems:")
    coverage = source_api.get_concept_coverage(source, source_id, return_indented=True)
    logger.info(f"Concept Coverage: {coverage}")
    sys.stdout.flush()

    ############################
    # Aggregate Children by Attribute
    ############################
    logger.info(
        "Aggregating children of the concept by a specific attribute (replace with actual attribute):"
    )
    # https://www.nlm.nih.gov/research/umls/knowledge_sources/metathesaurus/release/attribute_names.html

    aggregated_children = source_api.aggregate_children_by_attribute(
        source, source_id, "CTV3ID", return_indented=True
    )
    logger.info(f"Aggregated Children by Attribute:\n {aggregated_children}")
    sys.stdout.flush()

    #############################
    # Retrieve Full Hierarchy Recursively
    #############################
    logger.info(
        "Recursively fetching the full hierarchy for the concept (parents and children):"
    )
    full_hierarchy = source_api.get_full_hierarchy_recursive(
        source,
        source_id,
        depth=1,
        return_indented=True,
        save_to_file=True,
        file_path="full_hierarchy_output.txt",
    )
    logger.info(f"Full Recursive Hierarchy:{full_hierarchy} ")
    sys.stdout.flush()
