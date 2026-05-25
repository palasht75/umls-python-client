import os

from umls_python_client import UMLSClient


def main() -> None:
    client = UMLSClient(api_key=os.environ["UMLS_API_KEY"])
    response = client.search_api.search(
        search_string="diabetes",
        semantic_groups="Disorders",
        page_size=5,
    )
    print(response)


if __name__ == "__main__":
    main()
