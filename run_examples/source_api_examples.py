import os

from umls_python_client import TypedUMLSClient


def main() -> None:
    with TypedUMLSClient(api_key=os.environ["UMLS_API_KEY"]) as client:
        response = client.source_api.get_source_concept("SNOMEDCT_US", "73211009")
        print(response.result)


if __name__ == "__main__":
    main()
