# Usage

See https://www.launchableinc.com/docs/resources/cli-reference/ and
https://www.launchableinc.com/docs/getting-started/.

# Development

## Preparation

We recommend uv for dependency management:

```shell
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

In order to automatically format files with autopep8, this repository contains a
configuration for [pre-commit](https://pre-commit.com). Install the hook with
`uv run pre-commit install`.

## Load development environment

```shell
# Activate virtual environment
source .venv/bin/activate
# or use uv run for individual commands
uv run <command>
```

## Run tests cli

```shell
# Using poethepoet (recommended)
uv run poe test

# Direct command
uv run python -m unittest
```

## Run tests exe_deploy.jar

```
bazel test ...
```

## Available Development Tasks

This project uses [poethepoet](https://poethepoet.natn.io/) for task management. Available tasks:

```shell
# Show all available tasks
uv run poe --help

# Run tests
uv run poe test

# Run tests with XML output
uv run poe test-xml

# Run linting
uv run poe lint

# Run type checking
uv run poe type

# Format code
uv run poe format

# Build package
uv run poe build

# Install package locally
uv run poe install
```

## Add dependency

```shell
# Add runtime dependency
uv add some-package

# Add development dependency  
uv add --dev some-dev-package
```

## Updating Python Version

When updating the Python version requirement, update the following files:

1. **`.python-version`** - Used by pyenv, uv, and local development
2. **`pyproject.toml`** - Update `requires-python = ">=X.Y"`
3. **`setup.cfg`** - Update `python_requires = >=X.Y`
4. **`.github/workflows/python-package.yml`** - Update `python-version: ["X.Y"]`
5. **`.github/workflows/python-publish.yml`** - Update `uv python install X.Y`
6. **`README.md`** - Update prerequisite section
7. **`CLAUDE.md`** - Update development notes

# How to release

Create new release on Github, then Github Actions automatically uploads the
module to PyPI.

## How to update launchable/jar/exe_deploy.jar

```
./build-java.sh
```

# Installing CLI

You can install the `launchable` command from either source or [pypi](https://pypi.org/project/launchable/).

## Prerequisite

- \>= Python 3.13
- \>= Java 8

## Install from source

```sh
$ pwd
~/cli

$ python setup.py install
```

## Install from pypi

```sh
$ pip3 install --user --upgrade launchable~=1.0
```

## Versioning

This module follows [Semantic versioning](https://semver.org/) such as X.Y.Z.

* Major (X)
  * Drastic update breaking backward compatibility
* Minor (Y)
  * Add new plugins, options with backward compatibility
* Patch (Z)-
  * Fix bugs or minor behaviors
