# UMLS Python Client

Production-ready Python client for the NLM UMLS REST APIs.

The package keeps the original `UMLSClient` behavior for existing users and adds
typed sync and async clients for new applications.

## Installation

```bash
pip install umls-python-client
```

Development install:

```bash
pip install ".[dev]"
```

## Authentication

UMLS requests require an API key from NLM:
https://documentation.uts.nlm.nih.gov/rest/authentication.html

```python
import os

api_key = os.environ["UMLS_API_KEY"]
```

## Legacy Compatible Usage

`UMLSClient` preserves the existing JSON formatting defaults and camelCase
namespaces.

```python
from umls_python_client import UMLSClient

client = UMLSClient(api_key="YOUR_API_KEY")

results = client.searchAPI.search(
    search_string="diabetes",
    semantic_types="T047",
    semantic_groups="Disorders",
)
print(results)

raw_results = client.search_api.search(
    search_string="diabetes",
    return_indented=False,
)
```

## Typed Sync Usage

```python
from umls_python_client import TypedUMLSClient

with TypedUMLSClient(api_key="YOUR_API_KEY") as client:
    response = client.cui_api.get_cui_info("C0011849")
    concept = response.result
    print(concept.name)
```

Typed responses return `UMLSResponse[T]`. The original UMLS JSON is available
through `response.raw` or `response.to_dict()`, and RDF/Turtle is available with
`response.to_rdf()`.

## Async Usage

```python
from umls_python_client import AsyncUMLSClient


async def main() -> None:
    async with AsyncUMLSClient(api_key="YOUR_API_KEY") as client:
        response = await client.search_api.search("diabetes", page_size=5)
        print(response.result)
```

## API Namespaces

| Namespace | Legacy alias | Coverage |
| --- | --- | --- |
| `search_api` | `searchAPI` | `/search/{version}`, including `semanticTypes` and `semanticGroups` |
| `cui_api` | `cuiAPI` | CUI detail, atoms, preferred atom, definitions, relations |
| `source_api` | `sourceAPI` | Source concepts, atoms, preferred atom, hierarchy, attributes, relations |
| `atom_api` | none | AUI detail and hierarchy endpoints |
| `crosswalk_api` | `crosswalkAPI` | Source identifier crosswalk |
| `semantic_network_api` | `semanticNetworkAPI` | Semantic type lookup |
| `metadata_api` | none | `/metadata/{version}/sources` |

## Output Behavior

Legacy methods support:

- `format="json"` or `format="rdf"`
- `return_indented=True` for pretty JSON strings
- `return_indented=False` for raw Python payloads
- `save_to_file=True` and `file_path="output-directory"`

Typed methods raise structured exceptions on failures:

- `UMLSRequestError`
- `UMLSHTTPError`
- `UMLSDecodeError`

## Current NLM API Notes

The Search API changed on May 4, 2026. This client supports the current
`semanticTypes` and `semanticGroups` filters and does not send obsolete
`pageNumber` pagination parameters for endpoints where the current NLM docs no
longer document pagination.

Official UMLS REST documentation:
https://documentation.uts.nlm.nih.gov/rest/home.html

## Testing

```bash
ruff check .
ruff format --check .
mypy src
pytest
python -m build
```

Live integration tests are optional and must be explicitly enabled by setting
`UMLS_API_KEY`; default CI uses mocked transports only.

## License

Apache-2.0. See `LICENSE`.
