import os

from umls_python_client import TypedUMLSClient


def main() -> None:
    with TypedUMLSClient(api_key=os.environ["UMLS_API_KEY"]) as client:
        response = client.crosswalk_api.get_crosswalk(
            source="HPO",
            id="HP:0001947",
            target_source="SNOMEDCT_US",
        )
        print(response.result)


if __name__ == "__main__":
    main()
