# UMLS Python Client

Production-ready Python SDK for the National Library of Medicine UMLS
Terminology Services APIs.

`umls-python-client` keeps the original `UMLSClient` interface for existing
users and adds typed sync, async, export, release, and workflow helpers for new
applications. It is designed for developers and researchers who need a practical
one-stop Python client for UMLS search, concepts, source vocabularies, semantic
types, crosswalks, metadata, and UTS release downloads.

## Why This Client

- Current NLM REST coverage, including the May 4, 2026 search filters
  `semanticTypes` and `semanticGroups`.
- Typed sync and async clients built on `httpx`.
- Backward-compatible legacy client with the original camelCase namespaces.
- Structured exceptions for modern clients and legacy error payloads for older
  code.
- JSON, JSONL, CSV, and RDF/Turtle exports.
- Practical helpers for bulk search, bulk crosswalk, concept profiles, source
  lookup, UMLS URL following, API-key validation, and release downloads.
- CI across Python 3.9 through 3.14.

## Installation

```bash
pip install umls-python-client
```

For local development:

```bash
pip install ".[dev,docs]"
```

## Authentication

Most UMLS requests require an API key from your UTS profile:
https://documentation.uts.nlm.nih.gov/rest/authentication.html

```python
import os

api_key = os.environ["UMLS_API_KEY"]
```

The metadata sources endpoint is public and does not require authentication,
but the client still uses one consistent client configuration.

## Typed Sync Quickstart

```python
from umls_python_client import TypedUMLSClient

with TypedUMLSClient(api_key="YOUR_UMLS_API_KEY") as client:
    response = client.search_api.search(
        "diabetes",
        semantic_groups="Disorders",
        page_size=25,
    )

    for result in response.result:
        print(result.ui, result.name)
```

Typed methods return `UMLSResponse[T]`. Use `response.result` for parsed
models, `response.raw` or `response.to_dict()` for the original UMLS envelope,
and `response.to_rdf()` for Turtle RDF.

## Async Quickstart

```python
from umls_python_client import AsyncUMLSClient


async def main() -> None:
    async with AsyncUMLSClient(api_key="YOUR_UMLS_API_KEY") as client:
        response = await client.crosswalk_api.get_crosswalk(
            source="HPO",
            id="HP:0001947",
            target_source="SNOMEDCT_US",
        )
        print(response.result)
```

## Legacy Compatible Usage

`UMLSClient` keeps existing imports, JSON string defaults, and camelCase
namespaces:

```python
from umls_python_client import UMLSClient

client = UMLSClient(api_key="YOUR_UMLS_API_KEY")

pretty_json = client.searchAPI.search("diabetes")
raw_dict = client.search_api.search("diabetes", return_indented=False)
rdf = client.cui_api.get_cui_info("C0011849", format="rdf")
```

Existing namespaces are preserved:

- `client.searchAPI`
- `client.sourceAPI`
- `client.cuiAPI`
- `client.semanticNetworkAPI`
- `client.crosswalkAPI`
- `client.metadataAPI`
- `client.atomAPI`
- `client.authAPI`
- `client.releaseAPI`

Modern namespaces are also available:

- `search_api`
- `source_api`
- `cui_api`
- `semantic_network_api`
- `crosswalk_api`
- `metadata_api`
- `atom_api`
- `auth_api`
- `release_api`

## Common Recipes

### Semantic Search

```python
response = client.search_api.search(
    "depression",
    semantic_types="T047|T046",
    semantic_groups="Disorders",
)
```

`semantic_types` supports semantic type TUIs, semantic type names, and semantic
tree number prefixes. Use pipes for multiple values, matching NLM's search
documentation.

### Source Code To CUI

```python
response = client.search_api.search(
    "9468002",
    input_type="sourceUi",
    search_type="exact",
    sabs="SNOMEDCT_US",
)
```

### HPO To SNOMED CT Crosswalk

```python
response = client.crosswalk_api.get_crosswalk(
    source="HPO",
    id="HP:0001947",
    target_source="SNOMEDCT_US",
)
```

UMLS CUI crosswalks are useful starting points for mapping work. Review results
before using them in clinical or research pipelines.

### Concept Profile

```python
profile = client.cui_api.get_concept_profile(
    "C0011849",
    include_atoms=False,
).result

print(profile.concept.name)
print([definition.value for definition in profile.definitions])
```

Concept profiles fetch all documented definition and relation pages by default.
Pass `all_pages=False` to keep the older first-page-only behavior.

### Metadata Lookup

```python
sources = client.metadata_api.find_source(abbreviation="SNOMEDCT_US").result
```

### Bulk Workflows

```python
searches = client.search_api.bulk_search(["diabetes", "asthma"])
crosswalks = client.crosswalk_api.bulk_crosswalk(
    ["HP:0001947", "HP:0001250"],
    source="HPO",
    target_source="SNOMEDCT_US",
)
```

### Follow UMLS URLs

Many UMLS payload fields contain URLs to related resources. Follow those URLs
with the same authenticated client:

```python
concept = client.cui_api.get_cui_info("C0011849").result
atoms = client.follow_url(concept.raw["atoms"])
```

Authenticated URL following is restricted to trusted UMLS/UTS hosts so an API
key is never attached to arbitrary third-party URLs.

### Release Downloads

```python
releases = client.release_api.list_releases(
    release_type="umls-full-release",
    current=True,
)

client.release_api.download_file(
    url=releases.result[0].url,
    path="downloads",
)
```

Call `list_releases()` without a `release_type` to inspect NLM's release
catalog, or pass a release type such as `umls-full-release` to discover current
download URLs.

## Exports

Typed responses can save themselves:

```python
response = client.search_api.search("fracture", page_size=25)

response.save("exports/search", format="jsonl")
response.save("exports/search.csv", format="csv")
response.save("exports/search.ttl", format="rdf")
```

Clients can export any response or raw payload:

```python
client.export(response, "exports/search.json", format="json", overwrite=True)
```

Supported formats:

| Format | Output |
| --- | --- |
| `json` | Full UMLS response envelope |
| `jsonl` | One result record per line |
| `csv` | Flattened scalar result fields |
| `rdf` | Turtle RDF |

If the path has a file suffix, the client writes exactly there. If the path is
a directory or suffixless path, parent directories are created and a safe
filename is generated.

Legacy `save_to_file=True` still works and now delegates to the same export
implementation.

## Endpoint Coverage

| Namespace | Coverage | Pagination behavior |
| --- | --- | --- |
| `search_api` | `/search/{version}` with semantic filters | Sends `pageSize`; no obsolete `pageNumber` |
| `metadata_api` | `/metadata/{version}/sources` | No auth required |
| `cui_api` | CUI detail, atoms, preferred atom, definitions, relations | Pagination where NLM documents it |
| `atom_api` | AUI detail, parents, children, ancestors, descendants | Sends `pageSize`; no `pageNumber` |
| `source_api` | Source detail, atoms, preferred atom, hierarchy, attributes, relations | Pagination where NLM documents it |
| `crosswalk_api` | Source identifier crosswalk | Supports documented pagination |
| `semantic_network_api` | Semantic type lookup | Single resource |
| `auth_api` | UMLS license/API-key validation | UTS validation endpoint |
| `release_api` | Release listing and authenticated downloads | UTS release/download endpoints |

## Error Handling

Typed clients raise structured exceptions:

- `UMLSRequestError`
- `UMLSHTTPError`
- `UMLSDecodeError`

Legacy `UMLSClient` methods keep returning error payload dictionaries instead
of raising for UMLS request failures.

Configure timeouts and retries at client construction:

```python
client = TypedUMLSClient(
    api_key="YOUR_UMLS_API_KEY",
    timeout=20.0,
    retries=3,
)
```

## Testing

```bash
ruff check .
ruff format --check .
mypy src
pytest
mkdocs build --strict
python -m build
```

Live integration tests are optional and require `UMLS_API_KEY`. Tests that would
validate user keys or download release files remain opt-in and do not run in
default CI.

## Migration Notes

From `1.0.x` and `1.1.0`:

- Existing imports and `UMLSClient` behavior remain supported.
- Prefer `TypedUMLSClient` for new sync code.
- Prefer `AsyncUMLSClient` for async applications.
- Prefer `response.save(...)` or `client.export(...)` over new uses of
  `save_to_file=True`.
- Use snake_case namespaces in new code. CamelCase namespaces remain available
  for compatibility.

## Documentation

- NLM UMLS REST docs: https://documentation.uts.nlm.nih.gov/rest/home.html
- NLM auth docs: https://documentation.uts.nlm.nih.gov/rest/authentication.html
- Project source: https://github.com/palasht75/umls-python-client

## Releases

This repository uses Release Please and PyPI trusted publishing. Merged commits
should use Conventional Commit prefixes:

- `fix:` for patch releases
- `feat:` for minor releases
- `feat!:` or `fix!:` for major releases

Release Please opens a release PR. Merging that release PR creates the GitHub
Release, builds distributions, attaches artifacts, and publishes to PyPI.

GitHub Actions must be allowed to create release PRs, or the repository must
provide a `RELEASE_PLEASE_TOKEN` secret with PR permissions.

## License

Apache-2.0. See `LICENSE`.
