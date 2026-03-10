# UMLS Python Client

Production-ready Python client for the UMLS REST APIs.

## Features

- Unified client interface for Search, Source, CUI, Semantic Network, and Crosswalk APIs.
- Consistent request behavior (timeouts, parameter handling, and error payloads).
- JSON and RDF output support.
- Optional file output for any endpoint response.
- Compatible with modern Python packaging (`pyproject.toml`).

## Installation

```bash
pip install umls-python-client
```

From source:

```bash
pip install .
```

Development install:

```bash
pip install ".[dev]"
```

## Quick Start

```python
from umls_python_client import UMLSClient

client = UMLSClient(api_key="YOUR_API_KEY")

# Preferred snake_case namespace
results = client.search_api.search("diabetes", page_size=5)
print(results)

# Backward-compatible namespace still works
legacy_results = client.searchAPI.search("hypertension", page_size=5)
print(legacy_results)

# Configure request timeout (seconds)
fast_fail_client = UMLSClient(api_key="YOUR_API_KEY", timeout=10.0)
```

## API Namespaces

`UMLSClient` exposes these namespaces:

- `search_api` (`searchAPI`)
- `source_api` (`sourceAPI`)
- `cui_api` (`cuiAPI`)
- `semantic_network_api` (`semanticNetworkAPI`)
- `crosswalk_api` (`crosswalkAPI`)

The names in parentheses are backward-compatible aliases.

## Output Behavior

- `format="json"` (default): JSON output
- `format="rdf"`: RDF/Turtle output
- `return_indented=True`: pretty JSON string
- `return_indented=False`: raw Python object for JSON output

## File Output

Most methods support:

- `save_to_file=True`
- `file_path="path/to/output_dir"` (optional)

If `file_path` is omitted, output is written to the current working directory.

## Error Handling

Network and HTTP errors return structured payloads with:

- `error`
- `status_code` (when available)
- `message` (when available)

## Running Tests

```bash
python -m unittest discover -s tests -q
```

Or with pytest:

```bash
pytest
```

## Project Layout

```text
umls_python_client/
  baseAPI/
  searchAPI/
  sourceAPI/
  cuiAPI/
  semanticNetworkAPI/
  crosswalkAPI/
  utils/
tests/
run_examples/
```

## License

Apache-2.0. See `LICENSE`.
