# Endpoint Coverage

| Namespace | Endpoint family | Pagination behavior |
| --- | --- | --- |
| `search_api` | `/search/{version}` | Sends `pageSize`; does not send obsolete `pageNumber`. |
| `metadata_api` | `/metadata/{version}/sources` | No authentication required. |
| `cui_api` | `/content/{version}/CUI/{CUI}` | Single resource. |
| `cui_api` | CUI atoms and preferred atom | Sends `pageSize`; no `pageNumber`. |
| `cui_api` | CUI definitions and relations | Supports documented `pageNumber` and `pageSize`. |
| `atom_api` | AUI detail, parents, children, ancestors, descendants | Sends `pageSize`; no `pageNumber`. |
| `source_api` | Source detail, atoms, preferred atom | Source atoms send `pageSize`; no atom pagination. |
| `source_api` | Source parents, children, ancestors, descendants | Supports documented `pageNumber` and `pageSize`. |
| `source_api` | Source attributes and relations | Supports documented `pageNumber` and `pageSize`. |
| `crosswalk_api` | `/crosswalk/{version}/source/{source}/{id}` | Supports documented `pageNumber` and `pageSize`. |
| `semantic_network_api` | `/semantic-network/{version}/TUI/{id}` | Single resource. |
| `auth_api` | `https://utslogin.nlm.nih.gov/validateUser` | Text/JSON validation response. |
| `release_api` | `https://uts-ws.nlm.nih.gov/releases` and `/download` | Release list plus authenticated file downloads. |

The client accepts `version="current"` by default and supports explicit UMLS
release strings such as `2024AA` wherever NLM supports versioned URIs.
