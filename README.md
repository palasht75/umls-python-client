# umls-client

## Overview

This Python package provides an interface to interact with the Unified Medical Language System (UMLS) REST APIs. It enables users to search for terms, retrieve CUIs (Concept Unique Identifiers), access semantic networks, crosswalk vocabularies, and transform UMLS data into RDF format. The package offers a flexible and powerful interface to work with UMLS content in various formats.

### Key Features:
- Search UMLS terms via the **SearchAPI**.
- Retrieve source concepts, atoms, and hierarchical structures using the **SourceAPI**.
- Fetch semantic type information using **SemanticNetworkAPI**.
- Crosswalk vocabularies using CUIs via **CrosswalkAPI**.
- Transform UMLS JSON data to RDF format for use with semantic web technologies.
- Save API responses to files in structured formats.

---

## Table of Contents

1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [APIs and Usage](#apis-and-usage)
   - [SearchAPI](#searchapi)
   - [SourceAPI](#sourceapi)
   - [SemanticNetworkAPI](#semanticnetworkapi)
   - [CrosswalkAPI](#crosswalkapi)
4. [RDF Transformation](#rdf-transformation)
5. [Saving Outputs](#saving-outputs)
6. [GitHub Actions](#github-actions)
7. [License](#license)

---

## Installation

### Prerequisites:
- Python 3.x
- UMLS API Key (Sign up at [UMLS API](https://uts.nlm.nih.gov/uts/signup-login))

### Clone the Repository
```bash
git clone https://github.com/<your-repo-name>/umls-apis.git
cd umls-apis
