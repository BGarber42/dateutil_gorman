# Releasing

This project uses two GitHub Actions workflows:

- `ci.yaml` runs tests, linting, type-checking, build validation, coverage, and
  package smoke tests on pull requests and pushes to `main`.
- `publish.yaml` builds and publishes release artifacts for tagged releases and
  manual TestPyPI publishing.

## Versioning

Package versions are derived from Git tags through `hatch-vcs`.

- Release tags must use the form `vX.Y.Z`
- Example: `v0.1.4`

Tagged releases publish the exact tagged version.
Non-tag builds produce development-style versions from Git history.

## Release Checklist

1. Ensure `ci.yaml` is green on `main`.
2. Update release notes for the new version.
3. Create and push a signed or standard Git tag, for example:

```bash
git tag v0.1.4
git push origin v0.1.4
```

4. Wait for `publish.yaml` to build and validate the distribution.
5. Approve the `pypi` environment deployment in GitHub when prompted.
6. Confirm the package appears on PyPI.

## TestPyPI

To publish to TestPyPI:

1. Open the `Publish Python distributions` workflow in GitHub Actions.
2. Run the workflow manually with `workflow_dispatch`.
3. The workflow will build, validate, and publish to the `testpypi`
   environment automatically.

## PyPI Environment Approval

The workflow is configured to use the `pypi` GitHub environment. To enforce
manual approval before production publishing, configure required reviewers in:

- GitHub repository settings
- `Environments`
- `pypi`

## Validation Performed In CI

Each release candidate is validated with:

- `pytest`
- `pytest-cov`
- `ruff check .`
- `mypy src`
- `twine check dist/*`
- wheel smoke install
- sdist smoke install
