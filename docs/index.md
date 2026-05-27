# UMLS Python Client

`umls-python-client` is a typed Python SDK for the National Library of Medicine
UMLS Terminology Services APIs. It keeps the original `UMLSClient` interface and
adds modern sync, async, export, and workflow helpers for production projects.

## What It Covers

- UMLS search, CUI content, atoms, source identifiers, metadata, crosswalk, and
  semantic network endpoints.
- UTS license validation and release/download endpoints.
- Typed response models that preserve unknown fields from NLM.
- JSON, JSONL, CSV, and RDF/Turtle exports.
- Practical helpers for bulk search, bulk crosswalk, concept profiles, metadata
  lookup, URL following, and documented paginated endpoints.

## Install

```bash
pip install umls-python-client
```

```python
from umls_python_client import TypedUMLSClient

with TypedUMLSClient(api_key="YOUR_UMLS_API_KEY") as client:
    response = client.search_api.search(
        "diabetes",
        semantic_groups="Disorders",
    )
    for result in response.result:
        print(result.ui, result.name)
```

## API Key

UMLS API calls require an API key from your UTS profile. The metadata sources
endpoint does not require authentication, but the client still accepts the same
client configuration for a consistent API.
