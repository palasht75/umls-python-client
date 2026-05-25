import os

from umls_python_client import TypedUMLSClient


def main() -> None:
    with TypedUMLSClient(api_key=os.environ["UMLS_API_KEY"]) as client:
        response = client.semantic_network_api.get_semantic_type("T047")
        print(response.result)


if __name__ == "__main__":
    main()
