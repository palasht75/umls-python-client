import json
import logging
from rdf.json_to_rdf import convert_to_rdf


logger = logging.getLogger(__name__)

def handle_response_with_format(response, format: str = "json", return_indented: bool = True) -> str:
    """
    Generalized function to handle response based on the requested format.
    
    Args:
        response: The API response to handle.
        format (str): The format in which the response should be returned. Can be 'json' or 'rdf'.
        return_indented (bool): Whether to return indented JSON. Ignored if format is 'rdf'.

    Returns:
        str: The formatted response as a string in either JSON or RDF.
    """
    try:
        # Handle JSON format
        if format == "json":
            if return_indented:
                return json.dumps(response, indent=4)
            else:
                return response
        
        # Handle RDF format
        elif format == "rdf":
            try:
                json_data = response
                return convert_to_rdf(json_data=json_data)  # Assuming convert_to_rdf is available
            except Exception as e:
                logger.error(f"An error occurred while converting to RDF: {e}. Falling back to JSON.")
                # Fallback to JSON in case of RDF conversion error
                return json.dumps(response, indent=4)
        
        # Handle unsupported format
        else:
            logger.error(f"Unsupported format: {format}. Returning JSON as default.")
            return json.dumps(response, indent=4)

    except Exception as e:
        logger.error(f"An error occurred while handling the response: {e}. Returning raw response.")
        return str(response)

