"""Dagger functions for building and publishing Python distributions."""

from typing import Annotated

import dagger
from dagger import Doc, dag, function, object_type


DEFAULT_PYPI_URL = "https://upload.pypi.org/legacy/"


@object_type
class PypiPublisher:
    """Build Python distributions with uv and upload them to a PyPI index."""

    @function
    def build(
        self,
        source: Annotated[dagger.Directory, Doc("Project directory containing pyproject.toml")],
        python_version: Annotated[
            str,
            Doc("Python image tag used to build the distribution"),
        ] = "3.13",
    ) -> dagger.Directory:
        """Build a wheel and source distribution and return them as a directory.

        The project is supplied explicitly instead of being read from the
        module's working directory. This lets the module publish any Python
        project, locally or from another Dagger pipeline.
        """
        return (
            dag.container()
            .from_(f"python:{python_version}-slim")
            .with_exec(["pip", "install", "--no-cache-dir", "uv"])
            .with_mounted_directory("/src", source)
            .with_workdir("/src")
            .with_exec(["uv", "build", "--out-dir", "/dist"])
            .directory("/dist")
        )

    @function
    async def publish(
        self,
        source: Annotated[dagger.Directory, Doc("Project directory containing pyproject.toml")],
        pypi_token: Annotated[dagger.Secret, Doc("PyPI API token")],
        repository_url: Annotated[
            str,
            Doc("Upload endpoint, for example TestPyPI's legacy endpoint"),
        ] = DEFAULT_PYPI_URL,
        python_version: Annotated[
            str,
            Doc("Python image tag used to build the distribution"),
        ] = "3.13",
    ) -> str:
        """Build the project and upload its wheel and sdist to a PyPI index."""
        artifacts = self.build(source=source, python_version=python_version)
        return await self.publish_artifacts(
            artifacts=artifacts,
            pypi_token=pypi_token,
            repository_url=repository_url,
        )

    @function
    async def publish_artifacts(
        self,
        artifacts: Annotated[
            dagger.Directory,
            Doc("Directory containing only wheel and source-distribution artifacts"),
        ],
        pypi_token: Annotated[dagger.Secret, Doc("PyPI API token")],
        repository_url: Annotated[
            str,
            Doc("Upload endpoint, for example TestPyPI's legacy endpoint"),
        ] = DEFAULT_PYPI_URL,
    ) -> str:
        """Upload already-built artifacts to a PyPI-compatible index.

        ``pypi_token`` remains a Dagger Secret throughout the call and is not
        written to the artifact directory or included in command output.
        """
        await (
            dag.container()
            .from_("python:3.13-slim")
            .with_exec(["pip", "install", "--no-cache-dir", "uv"])
            .with_mounted_directory("/dist", artifacts)
            .with_secret_variable("PYPI_TOKEN", pypi_token)
            .with_env_variable("PYPI_REPOSITORY_URL", repository_url)
            .with_workdir("/dist")
            .with_exec(
                [
                    "/bin/sh",
                    "-ec",
                    'set -- ./*.whl ./*.tar.gz; test -f "$1"; '
                    'uv publish --publish-url "$PYPI_REPOSITORY_URL" '
                    '--token "$PYPI_TOKEN" "$@"',
                ]
            )
            .sync()
        )
        return f"Published artifacts to {repository_url}"
