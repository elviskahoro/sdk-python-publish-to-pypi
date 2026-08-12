"""Black-box tests for the pypi-publisher Dagger module."""

import dagger
from dagger import dag, function, object_type


_PYPROJECT = """\
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "example-package"
version = "0.1.0"
requires-python = ">=3.9"
"""


@object_type
class Tests:
    """Exercises the installed pypi-publisher dependency as a caller would."""

    @function
    async def build_produces_wheel_and_sdist(self) -> None:
        """Build returns exactly the standard wheel and source-distribution files."""
        source = (
            dag.directory()
            .with_new_file("pyproject.toml", _PYPROJECT)
            .with_new_file("example_package/__init__.py", "")
        )
        artifacts = await dag.pypi_publisher().build(source=source).entries()

        if not any(name.endswith(".whl") for name in artifacts):
            raise RuntimeError(f"Expected a wheel; got {artifacts}")
        if not any(name.endswith(".tar.gz") for name in artifacts):
            raise RuntimeError(f"Expected a source distribution; got {artifacts}")

    @function
    async def all(self) -> None:
        """Run every module test."""
        await self.build_produces_wheel_and_sdist()
