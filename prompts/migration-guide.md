# PyPI publisher migration prompt

Copy the prompt below into an agent working in a Python SDK repository.

```text
Migrate this repository to use the reusable Python Dagger PyPI publisher
module:

  github.com/elviskahoro/sdk-python-publish-to-pypi@main

First read the repository's AGENTS.md and follow it. Inspect the worktree
before editing. Preserve unrelated user changes; if a required file already
has conflicting uncommitted edits, stop and report the exact conflict instead
of overwriting it. Do not commit, push, create releases, or publish to PyPI
unless I explicitly ask.

Understand the shared module before making changes:

* `build --source <directory>` builds a conventional Python project with uv
  and returns a wheel plus sdist.
* `publish --source <directory> --pypi-token env:PYPI_TOKEN` builds then
  publishes a conventional project using a Dagger Secret.
* `publish-artifacts --artifacts <directory> --pypi-token env:PYPI_TOKEN`
  publishes prebuilt `*.whl` and `*.tar.gz` artifacts. Use this whenever the
  repository has custom build logic, produces multiple distributions, or
  needs a separate build stage.

Migration requirements:

1. Preserve the repository's existing build semantics. Do not replace custom
   staging, metadata rewriting, code generation, tests, version validation,
   or multi-package builds with the shared module's simple `build` function.
   In those cases, keep the existing build and route its final `dist/`
   directory through `publish-artifacts`.
2. Replace direct `uv publish`, `twine upload`, and any plain-text token
   plumbing with the shared module. Tokens must be passed only as Dagger
   secrets, e.g. `--pypi-token env:PYPI_TOKEN`; never echo, write, or add a
   token to arguments, source, artifacts, or logs.
3. Preserve PyPI Trusted Publishing workflows. If GitHub Actions already uses
   `pypa/gh-action-pypi-publish` with `id-token: write`, keep that upload step:
   it uses GitHub OIDC rather than an API token. Use the shared module to build
   or token-publish only where that authentication model is appropriate.
4. Ensure any release script builds artifacts once, clears or replaces stale
   `dist/` contents safely, and invokes the module with the artifacts it just
   produced. Keep shell safety (`set -euo pipefail`) and quote variables.
5. Update usage docs and CI comments with the new command. Use the fully
   qualified Git module reference above, not a developer-specific local path.
6. Add or update focused tests. At minimum, validate the build path produces
   a wheel and an sdist (and every expected package for multi-package builds).
   Do not invoke a real PyPI upload during tests.
7. Validate all changed Python/shell/YAML syntax and run the repository's
   relevant existing checks. Report the exact commands and results.

For a repository that builds its own artifacts, the resulting publish command
should be equivalent to:

  dagger -m github.com/elviskahoro/sdk-python-publish-to-pypi@main \
    call publish-artifacts \
    --artifacts ./dist \
    --pypi-token env:PYPI_TOKEN

For a conventional one-distribution Python project, it can instead be:

  dagger -m github.com/elviskahoro/sdk-python-publish-to-pypi@main \
    call publish \
    --source . \
    --pypi-token env:PYPI_TOKEN

Finish with a concise summary of changed files, preserved release behavior,
and validation. Do not publish anything.
```
