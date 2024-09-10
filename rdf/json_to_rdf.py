from rdflib import Graph, Literal, Namespace, URIRef


def convert_to_rdf(
    json_data: dict, namespace_url: str = "http://example.org/umls#"
) -> str:
    """
    Convert the UMLS JSON data to RDF format dynamically, handling both lists and dictionaries in the 'result' field.

    Args:
        json_data (dict): The JSON response from any UMLS API.
        namespace_url (str): The base namespace URL for RDF generation. Defaults to "http://example.org/umls#".

    Returns:
        str: The RDF data in Turtle format.
    """
    # Initialize the RDF graph
    g = Graph()

    # Define the UMLS namespace
    UMLS = Namespace(namespace_url)

    # Check if 'result' is a list or a dictionary
    result_data = json_data.get("result", [])

    if isinstance(result_data, dict):
        # Handle single dictionary case
        add_triples_from_dict(g, result_data, UMLS)
    elif isinstance(result_data, list):
        # Handle list of results
        for item in result_data:
            if isinstance(item, dict):
                add_triples_from_dict(g, item, UMLS)
            else:
                # Log or handle non-dictionary items if needed
                print("Skipping non-dictionary item in result list")

    # Serialize the RDF graph to a string in Turtle format
    rdf_data = g.serialize(format="turtle")
    return rdf_data


def add_triples_from_dict(g: Graph, data: dict, UMLS: Namespace):
    """
    Helper function to add RDF triples from a dictionary of data.

    Args:
        g (Graph): The RDF graph.
        data (dict): The dictionary to process.
        UMLS (Namespace): The RDF namespace.
    """
    # Use the 'ui' or 'concept' field as the subject URI, fallback to a generic URI if not available
    subject_uri = URIRef(data.get("concept", f"{UMLS}unknown_concept"))

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
    ]

    # Iterate over common fields and dynamically add RDF triples if the field exists and is not "NONE"
    for field in common_fields:
        field_value = data.get(field)
        if field_value and field_value != "NONE":  # Skip None or "NONE" values
            if isinstance(field_value, str) and field_value.startswith(
                "http"
            ):  # If it's a URL
                g.add((subject_uri, UMLS[field], URIRef(field_value)))
            else:
                g.add((subject_uri, UMLS[field], Literal(field_value)))

    # Handle any additional fields not covered in 'common_fields' (for flexibility)
    for field, value in data.items():
        if field not in common_fields and value and value != "NONE":
            if isinstance(value, str) and value.startswith("http"):  # If it's a URL
                g.add((subject_uri, UMLS[field], URIRef(value)))
            else:
                g.add((subject_uri, UMLS[field], Literal(value)))
