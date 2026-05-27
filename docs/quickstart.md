# Quickstart

## Typed Sync Client

```python
import os

from umls_python_client import TypedUMLSClient

with TypedUMLSClient(api_key=os.environ["UMLS_API_KEY"]) as client:
    concept = client.cui_api.get_cui_info("C0011849").result
    print(concept.name)
```

## Async Client

```python
import os

from umls_python_client import AsyncUMLSClient


async def main() -> None:
    async with AsyncUMLSClient(api_key=os.environ["UMLS_API_KEY"]) as client:
        response = await client.crosswalk_api.get_crosswalk(
            source="HPO",
            id="HP:0001947",
            target_source="SNOMEDCT_US",
        )
        print(response.result)
```

## Legacy Compatible Client

```python
from umls_python_client import UMLSClient

client = UMLSClient(api_key="YOUR_UMLS_API_KEY")

payload_as_json_string = client.searchAPI.search("diabetes")
payload_as_dict = client.search_api.search("diabetes", return_indented=False)
```

The legacy client keeps camelCase namespaces and JSON string defaults for older
applications. New code should prefer `TypedUMLSClient` or `AsyncUMLSClient`.

## Exports

```python
from umls_python_client import TypedUMLSClient

with TypedUMLSClient(api_key="YOUR_UMLS_API_KEY") as client:
    response = client.search_api.search("fracture", page_size=25)
    response.save("exports/search-results", format="jsonl")
    client.export(response, "exports/search-results.csv", format="csv")
```
