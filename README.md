# Usage

See https://docs.launchableinc.com/cli-reference and https://docs.launchableinc.com/getting-started.

# Development
## Preparation
We recommend Pipenv
```shell
pip install pipenv
pipenv install --dev
```
If you mess up your local pipenv, `pipenv --rm` will revert the operation above.

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

## Versioning
This module follows [Semantic versioning](https://semver.org/) such as X.Y.Z.

* Major (X)
  * Drastic update breaking backward compatibility
* Minor (Y)
  * Add new plugins, options with backward compatibility
* Patch (Z)-
  * Fix bugs or minor behaviors
