# Usage

See https://docs.launchableinc.com/cli-reference and https://docs.launchableinc.com/getting-started.

# Development
## Preparation
We recommend Pipenv
```shell
pip install pipenv
pipenv install --dev
```

## Load development environment
```shell
pipenv shell
```

## Run tests
```shell
pipenv run test
```

## Add dependency
```shell
pipenv install --dev some-what-module
```

# How to release
Create new release on Github, then Github Actions automatically uploads the module to PyPI.
