import os

from umls_python_client import TypedUMLSClient


def main() -> None:
    with TypedUMLSClient(api_key=os.environ["UMLS_API_KEY"]) as client:
        response = client.cui_api.get_cui_info("C0011849")
        print(response.result)


if __name__ == "__main__":
    main()
