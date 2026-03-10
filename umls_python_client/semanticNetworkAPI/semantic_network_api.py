import logging
from typing import Optional

from umls_python_client.baseAPI.umls_api_base import UMLSAPIBase

logger = logging.getLogger(__name__)


class SemanticNetworkAPI(UMLSAPIBase):
    """
    A class to interact with the UMLS REST API's semantic network functionality, inheriting from UMLSAPIBase.

    The SemanticNetworkAPI class provides methods to retrieve semantic type information by its TUI (Type Unique Identifier).

    Attributes:
        api_key (str): The UMLS API key used for authentication (inherited from the UMLSAPIBase class).
        version (str): The version of the UMLS release to use (inherited from UMLSAPIBase).
    """

    def get_semantic_type(
        self,
        tui: str,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
        return_indented: bool = True,
        format: str = "json",
    ):
        """
        Retrieve information about a semantic type using its TUI (Type Unique Identifier).
        Args:
            tui (str): The TUI identifier for the semantic type you want to retrieve.
        Returns:
            dict: The semantic type information retrieved from the UMLS API.
        """
        logger.info("Fetching semantic type for TUI: %s", tui)
        return self._request_formatted(
            path=f"/semantic-network/{self.version}/TUI/{tui}",
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"semantic_type_{tui}.txt",
        )
