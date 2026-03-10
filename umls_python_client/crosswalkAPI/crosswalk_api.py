import logging
from typing import Any, Optional

from umls_python_client.baseAPI.umls_api_base import UMLSAPIBase

logger = logging.getLogger(__name__)


class CrosswalkAPI(UMLSAPIBase):
    """
    A class to interact with the UMLS REST API's Crosswalk functionality, inheriting from UMLSAPIBase.

    The CrosswalkAPI class provides methods to retrieve crosswalk data between different vocabularies.

    Attributes:
        api_key (str): The UMLS API key used for authentication (inherited from the UMLSAPIBase class).
        version (str): The version of the UMLS release to use (inherited from UMLSAPIBase).
    """

    def get_crosswalk(
        self,
        source: str,
        id: str,
        target_source: Optional[str] = None,
        include_obsolete: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        """
        Retrieve crosswalk data between vocabularies using a UMLS source and identifier.

        Args:
            source (str): The source vocabulary abbreviation, such as 'HPO'.
            id (str): The identifier code from the source vocabulary, e.g., 'HP:0001947'.
            target_source (Optional[str], optional): The target vocabulary abbreviation, such as 'SNOMEDCT_US'. Defaults to None.
            include_obsolete (bool, optional): Determines whether to return obsolete codes. Defaults to False.
            page_number (int, optional): Specifies the page of results to fetch. Defaults to 1.
            page_size (int, optional): Specifies the number of results to include per page. Defaults to 25.
            return_indented (bool, optional): Whether to return the JSON indented. Defaults to True.
            format (str, optional): The format of the output. Can be 'json' or 'rdf'. Defaults to 'json'.
            save_to_file (bool, optional): Save output to a text file (True or False). Defaults to False.
            file_path (str, optional): Path to save the output file.

        Returns:
            Any: The response from the UMLS Crosswalk API in the specified format (JSON or RDF).
        """
        params = {
            "targetSource": target_source,
            "includeObsolete": str(include_obsolete).lower(),
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        logger.info(
            "Fetching crosswalk data for source=%s id=%s target=%s",
            source,
            id,
            target_source,
        )
        return self._request_formatted(
            path=f"/crosswalk/{self.version}/source/{source}/{id}",
            params=params,
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"crosswalk_{source}.txt",
        )
