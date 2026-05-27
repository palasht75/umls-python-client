# Releasing

This repository uses Release Please and PyPI trusted publishing.

## Normal Release Flow

1. Merge feature and fix PRs into `main` with Conventional Commit messages.
2. Release Please opens or updates a release PR.
3. Merge the release PR.
4. The release workflow creates the GitHub Release, builds distributions,
   attaches artifacts, and publishes to PyPI.

## Commit Types

- `fix:` creates a patch release.
- `feat:` creates a minor release.
- `feat!:` or `fix!:` creates a major release.

## Repository Settings

GitHub Actions must be allowed to create pull requests, or the repository must
provide a `RELEASE_PLEASE_TOKEN` secret with appropriate permissions.

PyPI trusted publishing must point at:

- Owner: `palasht75`
- Repository: `umls-python-client`
- Workflow: `release-please.yml`
- Environment: `pypi`
