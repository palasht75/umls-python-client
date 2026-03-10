import logging
from typing import Any, Dict, Optional, Union

from umls_python_client.baseAPI.umls_api_base import UMLSAPIBase

logger = logging.getLogger(__name__)


class CUIAPI(UMLSAPIBase):
    """
    The CUIAPI class is designed to interact with the UMLS REST API for Concept Unique Identifier (CUI) data retrieval.
    This class provides methods to fetch detailed information, atoms, definitions, and relations related to a given CUI.

    The CUIAPI class allows you to:
    - Retrieve detailed information about a CUI from the UMLS Metathesaurus.
    - Retrieve atoms (the smallest units of meaning) associated with a CUI.
    - Retrieve definitions tied to a given CUI.
    - Retrieve relationships (semantic relations between concepts) for a CUI.

    Attributes:
        api_key (str): The UMLS API key used for authentication (inherited from the UMLSAPIBase class).
        version (str): The version of the UMLS release to use (inherited from UMLSAPIBase).
        base_url (str): The base URL for UMLS API requests (inherited from UMLSAPIBase).
    """

    def get_cui_info(
        self,
        cui,
        return_indented: bool = True,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Fetches detailed information about the specified CUI from the UMLS Metathesaurus.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing the detailed information about the CUI.
        """

        logger.info("Fetching CUI concept: %s", cui)
        return self._request_formatted(
            path=f"/content/{self.version}/CUI/{cui}",
            output_format="json",
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"cui_info_{cui}.txt",
        )

    def get_atoms(
        self,
        cui: str,
        return_indented: bool = True,
        sabs: Optional[str] = None,
        ttys: Optional[str] = None,
        language: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Fetches atoms associated with the specified CUI.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing atoms related to the CUI.
        """
        params = {
            "sabs": sabs,
            "ttys": ttys,
            "language": language,
            "includeObsolete": str(include_obsolete).lower(),
            "includeSuppressible": str(include_suppressible).lower(),
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        logger.info("Fetching CUI atoms for: %s", cui)
        return self._request_formatted(
            path=f"/content/{self.version}/CUI/{cui}/atoms",
            params=params,
            output_format="json",
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"cui_atoms_{cui}.txt",
        )

    def get_definitions(
        self,
        cui: str,
        return_indented: bool = True,
        sabs: Optional[str] = None,
        page_number: int = 1,
        page_size: int = 25,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Fetches definitions associated with the specified CUI.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing definitions tied to the CUI.
        """
        params = {
            "sabs": sabs,
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        logger.info("Fetching CUI definitions for: %s", cui)
        return self._request_formatted(
            path=f"/content/{self.version}/CUI/{cui}/definitions",
            params=params,
            output_format="json",
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"cui_definitions_{cui}.txt",
        )

    def get_relations(
        self,
        cui,
        return_indented: bool = True,
        sabs: Optional[str] = None,
        include_relation_labels: Optional[str] = None,
        include_additional_labels: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Union[str, Dict[str, Any]]:
        """
        Fetches relationships for the specified CUI.
        - Parameters:
            - cui (str): The Concept Unique Identifier (CUI) to query.
        - Returns:
            - A dictionary containing the relationships of the CUI.
        """
        params = {
            "sabs": sabs,
            "includeRelationLabels": include_relation_labels,
            "includeAdditionalRelationLabels": include_additional_labels,
            "includeObsolete": str(include_obsolete).lower(),
            "includeSuppressible": str(include_suppressible).lower(),
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        logger.info("Fetching CUI relations for: %s", cui)
        return self._request_formatted(
            path=f"/content/{self.version}/CUI/{cui}/relations",
            params=params,
            output_format="json",
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"cui_relations_{cui}.txt",
        )
