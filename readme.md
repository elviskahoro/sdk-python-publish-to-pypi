# Dagger PyPI publisher

A reusable Dagger module that builds a Python project with `uv` and publishes
its wheel and source distribution to PyPI or another compatible index.

The source project is an explicit `Directory` argument, so this module can be
called from any repository or composed into another Dagger pipeline. The PyPI
credential is a Dagger `Secret`; it is never copied into the project or
artifacts.

## Functions

- `build` builds a project and returns its `dist/` artifacts.
- `publish` builds a project and uploads the artifacts.
- `publish-artifacts` uploads prebuilt artifacts. Use this when build and
  release happen in separate pipeline stages.

## Local use

Run these commands from the Python project you want to publish. Replace
`<module-ref>` with this module's local path, a vendored path, or a published
Git module reference such as `github.com/OWNER/sdk-python-publish-to-pypi@main`.

```sh
# Inspect the available arguments and descriptions.
dagger -m <module-ref> functions

# Build and export a wheel plus source distribution.
dagger -m <module-ref> call build \
  --source . \
  export --path dist

# Build and publish to PyPI. The token stays a Dagger secret.
dagger -m <module-ref> call publish \
  --source . \
  --pypi-token env:PYPI_TOKEN

# Publish existing artifacts instead.
dagger -m <module-ref> call publish-artifacts \
  --artifacts ./dist \
  --pypi-token env:PYPI_TOKEN
```

For TestPyPI, pass its upload endpoint explicitly:

```sh
dagger -m <module-ref> call publish \
  --source . \
  --pypi-token env:TEST_PYPI_TOKEN \
  --repository-url https://test.pypi.org/legacy/
```

## GitHub Actions

For PyPI Trusted Publishing, keep the upload step in GitHub Actions so PyPI
can validate GitHub's OIDC identity. This module remains useful for a
reproducible build; export its artifacts, then use PyPA's official action:

```yaml
permissions:
  contents: read
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    steps:
      - uses: actions/checkout@v6
      - uses: dagger/dagger-for-github@v8.4.1
      - run: >-
          dagger -m github.com/OWNER/sdk-python-publish-to-pypi@main call build
          --source . export --path dist
      - uses: pypa/gh-action-pypi-publish@release/v1
```

Use this module's `publish` function when a PyPI API token is the intended
authentication mechanism. It deliberately does not accept a token as plain
text.

## Development

This is a Python Dagger module: `dagger.json` declares the Python SDK and
`src/pypi_publisher/` contains its `@object_type` and `@function` API. The
nearby `tests/` directory is a second Python Dagger module that installs this
module as a dependency and exercises its public API.

```sh
# Validate the module API.
dagger functions

# Run all module tests.
dagger -m tests call all
```
