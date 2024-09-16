# Welcome to the UMLS Python Client

The **UMLS Python Client** is a comprehensive, modular, and user-friendly API client designed for healthcare developers and researchers. It offers seamless access to UMLS data, simplifying interactions with various healthcare terminologies and codes. Our client provides five distinct groups of APIs, encompassing every single REST API from UMLS with all query parameters and additional features.

## Why Choose UMLS Python Client

- **Modular Design**: Unlike other packages, our client is modular, providing separate APIs for each UMLS service. This modularity allows for easy integration and customization to meet your specific needs.

- **Comprehensive Coverage**: A one-stop destination that includes every UMLS REST API, ensuring you have access to all necessary endpoints and functionalities.

- **Enhanced Functionality**: Additional features like response formatting in RDF or JSON, file saving options, and extended functions built on top of existing endpoints enhance your development experience.

- **Best Practices Implementation**: Built using the latest best practices, including type hinting for improved code readability and proper error logging for easier debugging.

- **Future-Proof**: We promise support for all future changes to UMLS APIs, ensuring your projects remain up-to-date with the latest developments.

- **Comprehensive Documentation and Notebooks**: We provide detailed documentation and interactive Jupyter notebooks, which are not offered by others, to help you get started quickly and efficiently.

- **Open Source Collaboration**: Fully open for collaboration and improvement by the community. Your contributions are welcome to make this project even better.

## Available APIs

Our client divides all REST APIs into five main parts for better organization and ease of use:

### 1. Search API

Search for concepts using various parameters such as words, exact matches, and codes across UMLS terminologies.

- Perform basic, partial, and exact searches.
- Support for specific vocabularies like **SNOMEDCT_US**, **LOINC**, etc.
- Retrieve identifiers like CUIs and source-asserted identifiers.

### 2. CUI API

Retrieve information for Concept Unique Identifiers (CUIs) from the UMLS Metathesaurus.

- Get detailed information about specific CUIs.
- Fetch related atoms, ancestors, descendants, and relations for CUIs.

### 3. Source API

Fetch detailed information about source-asserted concepts or descriptors.

- Retrieve concepts and related terms from sources like **SNOMEDCT_US**, **LOINC**, and more.
- Access full hierarchies of concepts (ancestors, children, etc.).

### 4. Semantic Network API

Explore the UMLS Semantic Network and its relationships.

- Retrieve semantic type information for given TUIs (Type Unique Identifiers).
- Explore relationships between different semantic types.

### 5. Crosswalk API

Map codes between different terminologies and vocabularies in healthcare.

- Translate between various vocabularies like **SNOMED CT**, **ICD**, and **LOINC**.
- Facilitate interoperability between healthcare systems.

## Key Features

- **Automated Hierarchical Retrieval**: Fetch full hierarchies (ancestors, descendants) for any concept effortlessly.
- **Enhanced Response Formatting**: Convert UMLS data into RDF or JSON formats for semantic web applications and easy data manipulation.
- **File Output Support**: Save your API responses directly into files for easy storage and access.
- **Logging and Error Handling**: Track requests and responses with detailed logging and comprehensive error handling for invalid inputs, failed API requests, and more.
- **Type Hinting**: Code is written with type hints for better code readability and easier maintenance.
- **Customization**: Configure output formats and save data as needed to suit your workflow.

## How to Get Started

### 1. Install the Package

Install the UMLS Python Client using pip:

```bash
pip install umls-python-client
```

### 2. Initialize the Client

Initialize the `UMLSClient` with your API key:

```python
from umls_python_client import UMLSClient

api_key = "YOUR_API_KEY"
umls_client = UMLSClient(api_key=api_key)
```

### 3. Explore the APIs

You can explore the available APIs below:

| API Name               | Description                                      | Documentation Link                                             | Colab Notebook Link                                                                                                 |
|------------------------|--------------------------------------------------|----------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------|
| **SearchAPI**          | Search the UMLS database for terms and concepts. | <a href="https://palasht75.github.io/umls-python-client-homepage/searchAPI" target="_blank">/searchAPI</a>           | <a href="https://colab.research.google.com/drive/1E70yM0It0qjfV_qit2qX83e9NB39lOzq?usp=sharing" target="_blank">Open in Colab</a>                          |
| **CUIAPI**             | Retrieve Concept Unique Identifier information.  | <a href="https://palasht75.github.io/umls-python-client-homepage/CUIAPI" target="_blank">/CUIAPI</a>                 | <a href="https://colab.research.google.com/drive/1dYm8-K_ZqjjDFcTppQaVXqUyD7GINpx_?usp=sharing" target="_blank">Open in Colab</a>                          |
| **SourceAPI**          | Access source-specific content in UMLS.          | <a href="https://palasht75.github.io/umls-python-client-homepage/sourceAPI" target="_blank">/sourceAPI</a>           | <a href="https://colab.research.google.com/drive/1ICQFoZqfsW6YvcaoRo-DtZR2QAWmqFI0?usp=sharing" target="_blank">Open in Colab</a>                          |
| **SemanticNetworkAPI** | Explore semantic relationships.                  | <a href="https://palasht75.github.io/umls-python-client-homepage/semanticNetworkAPI" target="_blank">/semanticNetworkAPI</a> | <a href="https://colab.research.google.com/drive/1fax_gKwGuNl6SamHiCEZ2nHeuahm3_tX?usp=sharing" target="_blank">Open in Colab</a>                          |
| **CrosswalkAPI**       | Map concepts across vocabularies.                | <a href="https://palasht75.github.io/umls-python-client-homepage/crosswalkAPI" target="_blank">/crosswalkAPI</a>     | <a href="https://colab.research.google.com/drive/1XWu1c3HTUcxJTyHDootYGLw7GTUkEURM?usp=sharing" target="_blank">Open in Colab</a>                          |

*Click on the documentation links to learn more about each API and use the Colab notebooks to try them out interactively.*
## Example Usage

Here's a quick example of how to use the **SearchAPI** to find information about "diabetes":

```python
from umls_python_client import UMLSClient

api_key = "YOUR_API_KEY"

# Initialize the SearchAPI class with your API key
search_api = UMLSClient(api_key=api_key).searchAPI

#############################
# Perform a Basic Search
#############################
logger.info("Performing a basic search query for the term 'diabetes':")
search_results = search_api.search(
    search_string="diabetes"
)
print(f"Search Results for 'diabetes': {search_results}")
```

## Documentation and Resources

- **Full Documentation**: <a href="https://palasht75.github.io/umls-python-client-homepage/" target="_blank">Homepage</a>
- **UMLS REST APIs Home**: <a href="https://documentation.uts.nlm.nih.gov/rest/home.html" target="_blank">UMLS API Documentation</a>

## Contribute

We welcome contributions from the community! If you have any improvements or new ideas, feel free to open a pull request or an issue on our GitHub repository.

- <a href="https://palasht75.github.io/umls-python-client-homepage/contributors" target="_blank">Contributors</a>

## Support and Future Updates

We are committed to maintaining and updating this client to support all future changes in the UMLS APIs. If you encounter any issues or have feature requests, please open an issue on our [GitHub repository](https://github.com/palasht75/umls-python-client/issues).