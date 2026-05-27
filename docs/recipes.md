# Recipes

## Semantic Search

```python
response = client.search_api.search(
    "depression",
    semantic_types="T047|T046",
    semantic_groups="Disorders",
)
```

`semantic_types` accepts TUIs, semantic type names, or semantic tree number
prefixes. Use pipes when sending multiple values.

## Code To CUI

```python
response = client.search_api.search(
    "9468002",
    input_type="sourceUi",
    search_type="exact",
    sabs="SNOMEDCT_US",
)
```

## Crosswalk HPO To SNOMED CT

```python
response = client.crosswalk_api.get_crosswalk(
    source="HPO",
    id="HP:0001947",
    target_source="SNOMEDCT_US",
)
```

UMLS CUI crosswalk results are a starting point for curation. Review mappings
for clinical or research use.

## Concept Profile

```python
profile = client.cui_api.get_concept_profile(
    "C0011849",
    include_atoms=False,
).result

print(profile.concept.name)
print([definition.value for definition in profile.definitions])
```

## Metadata Lookup

```python
sources = client.metadata_api.find_source(abbreviation="SNOMEDCT_US").result
```

## Follow UMLS URLs

Many UMLS payload fields contain URLs to related resources. Follow them without
manually rebuilding request parameters:

```python
concept = client.cui_api.get_cui_info("C0011849").result
atoms = client.follow_url(concept.raw["atoms"])
```

## Release Downloads

```python
releases = client.release_api.list_releases(
    release_type="umls-full-release",
    current=True,
)
client.release_api.download_file(
    url=releases.result[0].url,
    path="downloads",
)
```

Call `list_releases()` without a `release_type` to inspect NLM's release
catalog. Pass a release type such as `umls-full-release` to discover current
download URLs before calling `download_file`.
