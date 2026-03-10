import json
import logging
from typing import Any

from umls_python_client.utils.json_to_rdf import convert_to_rdf

logger = logging.getLogger(__name__)


def handle_response_with_format(
    response: Any, format: str = "json", return_indented: bool = True
) -> Any:
    """Render API response in JSON or RDF."""
    if format not in {"json", "rdf"}:
        raise ValueError("Unsupported format. Use 'json' or 'rdf'.")

    if format == "json":
        if return_indented:
            if isinstance(response, str):
                return response
            return json.dumps(response, indent=4)
        return response

    try:
        if isinstance(response, str):
            response = json.loads(response)
        if not isinstance(response, dict):
            raise TypeError("RDF conversion requires dict-like JSON data.")
        return convert_to_rdf(json_data=response)
    except Exception:
        logger.warning(
            "An error occurred while converting to RDF. Falling back to JSON."
        )
        if format == "rdf":
            return json.dumps(response, indent=4)

    return str(response)
