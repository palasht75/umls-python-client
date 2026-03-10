import logging
from typing import Any, Dict

try:
    from rdflib import Graph, Literal, Namespace, URIRef
except ImportError:  # pragma: no cover - exercised only when optional dep is missing
    Graph = Literal = Namespace = URIRef = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


def convert_to_rdf(
    json_data: Dict[str, Any],
    namespace_url: str = "https://uts-ws.nlm.nih.gov/rest/content/#",
) -> str:
    """
    Convert the UMLS JSON data to RDF format dynamically, handling both lists and dictionaries in the 'result' field.

    Args:
        json_data (dict): The JSON response from any UMLS API.
        namespace_url (str): The base namespace URL for RDF generation. Defaults to "https://uts-ws.nlm.nih.gov/rest/content/#".

    Returns:
        str: The RDF data in Turtle format.
    """
    if Graph is None:
        raise RuntimeError("RDF output requires optional dependency 'rdflib'.")

    # Initialize the RDF graph
    g = Graph()

    # Define the UMLS namespace
    UMLS = Namespace(namespace_url)

    # Check if 'result' is a list or a dictionary
    result_data = json_data.get("result", [])

    if isinstance(result_data, dict):
        # Handle the case where 'result' is a dictionary with nested 'results' field (list)
        results_list = result_data.get("results", [])
        if isinstance(results_list, list):
            for item in results_list:
                if isinstance(item, dict):
                    add_triples_from_dict(g, item, UMLS)
        else:
            # If 'results' is not a list, treat it as a single concept dictionary
            add_triples_from_dict(g, result_data, UMLS)
    elif isinstance(result_data, list):
        # Handle the case where 'result' is directly a list
        for item in result_data:
            if isinstance(item, dict):
                add_triples_from_dict(g, item, UMLS)
            else:
                logger.warning("Skipping non-dictionary item in result list.")

    # Serialize the RDF graph to a string in Turtle format
    rdf_data = g.serialize(format="turtle")
    return rdf_data


def add_triples_from_dict(g: Graph, data: Dict[str, Any], umls: Namespace) -> None:
    """
    Helper function to add RDF triples from a dictionary of data.

    Args:
        g (Graph): The RDF graph.
        data (dict): The dictionary to process.
        umls (Namespace): The RDF namespace.
    """
    # Use the 'ui' or 'concept' field as the subject URI, fallback to a generic URI if not available
    if data.get("uri") is not None:
        subject_uri = URIRef(data.get("uri", f"{umls}unknown_concept"))
    else:
        subject_uri = URIRef(data.get("ui", f"{umls}unknown_concept"))

    # Define a list of key fields that are common across multiple UMLS APIs
    common_fields = [
        "ui",
        "name",
        "rootSource",
        "atomCount",
        "obsolete",
        "suppressible",
        "attributes",
        "atoms",
        "ancestors",
        "parents",
        "children",
        "descendants",
        "relations",
        "defaultPreferredAtom",
        "definitions",
        "uri",
        "rootSource",
    ]

    # Iterate over common fields and dynamically add RDF triples if the field exists and is not "NONE"
    for field in common_fields:
        field_value = data.get(field)
        if field_value and field_value != "NONE":  # Skip None or "NONE" values
            if isinstance(field_value, str) and field_value.startswith(
                "http"
            ):  # If it's a URL
                g.add((subject_uri, umls[field], URIRef(field_value)))
            else:
                g.add((subject_uri, umls[field], Literal(field_value)))

    # Handle any additional fields not covered in 'common_fields' (for flexibility)
    for field, value in data.items():
        if field not in common_fields and value and value != "NONE":
            if isinstance(value, str) and value.startswith("http"):  # If it's a URL
                g.add((subject_uri, umls[field], URIRef(value)))
            else:
                g.add((subject_uri, umls[field], Literal(value)))
