from importlib.metadata import PackageNotFoundError, version

from .crosswalkAPI.crosswalk_api import CrosswalkAPI
from .cuiAPI.cui_api import CUIAPI
from .searchAPI.search_api import SearchAPI
from .semanticNetworkAPI.semantic_network_api import SemanticNetworkAPI
from .sourceAPI.source_api import SourceAPI
from .umls_client import UMLSClient

try:
    __version__ = version("umls-python-client")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "UMLSClient",
    "SearchAPI",
    "SourceAPI",
    "CUIAPI",
    "SemanticNetworkAPI",
    "CrosswalkAPI",
    "__version__",
]
