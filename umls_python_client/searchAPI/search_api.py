import logging
from typing import Any, Optional

from umls_python_client.baseAPI.umls_api_base import UMLSAPIBase

logger = logging.getLogger(__name__)


class SearchAPI(UMLSAPIBase):
    """
    A class to interact with the UMLS REST API's search functionality, inheriting from UMLSAPIBase.

    The SearchAPI class provides methods to search for CUIs, source-asserted identifiers, and other UMLS-related data
    based on various query parameters such as search terms, source vocabularies, and return types.

    This class allows you to:
    - Return a list of CUIs and their names when searching a human-readable term.
    - Return a list of source-asserted identifiers (codes) and their names when searching a human-readable term.
    - Map source-asserted identifiers to UMLS CUIs.

    Attributes:
        api_key (str): The UMLS API key used for authentication (inherited from the UMLSAPIBase class).
        version (str): The version of the UMLS release to use (inherited from UMLSAPIBase).
    """

    def search(
        self,
        search_string: str,
        input_type: Optional[str] = None,
        include_obsolete: bool = False,
        include_suppressible: bool = False,
        return_id_type: str = "concept",
        sabs: Optional[str] = None,
        search_type: str = "words",
        partial_search: bool = False,
        page_number: int = 1,
        page_size: int = 25,
        return_indented: bool = True,
        format: str = "json",
        save_to_file: bool = False,
        file_path: Optional[str] = None,
    ) -> Any:
        """
        Perform a search query on the UMLS Metathesaurus.

        Parameters:
            search_string (str): The search term or code to search in UMLS.
            input_type (str, optional): Specifies the data type you are using as your search parameter.
                                        Valid values: 'atom', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi', 'tty'.
            include_obsolete (bool, optional): Return content that matches on obsolete terms. Default is False.
            include_suppressible (bool, optional): Return content that matches on suppressible terms. Default is False.
            return_id_type (str, optional): Specifies the type of identifier to retrieve. Default is 'concept'.
                                            Valid values: 'aui', 'concept', 'code', 'sourceConcept', 'sourceDescriptor', 'sourceUi'.
            sabs (str, optional): Comma-separated list of source vocabularies to include in your search.
                                  Use abbreviations of source vocabularies like 'SNOMEDCT_US'.
            search_type (str, optional): Type of search to perform. Default is 'words'.
                                         Valid values: 'exact', 'words', 'leftTruncation', 'rightTruncation', 'normalizedString', 'normalizedWords'.
            partial_search (bool, optional): Return partial matches for your query. Default is False.
            page_number (int, optional): Specifies the page of results to fetch. Default is 1.
            page_size (int, optional): Specifies the number of results to include per page. Default is 25.

        Returns:
            Any: The search results from the UMLS API.
        """

        params = {
            "string": search_string,
            "inputType": input_type,
            "includeObsolete": str(include_obsolete).lower(),
            "includeSuppressible": str(include_suppressible).lower(),
            "returnIdType": return_id_type,
            "sabs": sabs,
            "searchType": search_type,
            "partialSearch": str(partial_search).lower(),
            "pageNumber": page_number,
            "pageSize": page_size,
        }

        logger.info("Searching UMLS for '%s'", search_string)
        return self._request_formatted(
            path=f"/search/{self.version}",
            params=params,
            output_format=format,
            return_indented=return_indented,
            save_to_file=save_to_file,
            file_path=file_path,
            default_file_name=f"search_{search_string}.txt",
        )
