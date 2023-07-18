# Usage

See https://www.launchableinc.com/docs/resources/cli-reference/ and
https://www.launchableinc.com/docs/getting-started/.

# Development

## Preparation

We recommend Pipenv

```shell
pip install pipenv==2021.5.29
pipenv install --dev
```

Note that you will need to use 2021.5.29 as the Python version is fixed at 3.5,
and the Pipenv beyond that version won't support Python 3.5 or below.

If you mess up your local pipenv, `pipenv --rm` will revert the operation above.

In order to automatically format files with autopep8, this repository contains a
configuration for [pre-commit](https://pre-commit.com). Install the hook with
`pipenv run pre-commit install`.

## Load development environment

```shell
pipenv shell
```

## Run tests cli

```shell
pipenv run test
```

## Run tests exe_deploy.jar

```
bazel test ...
```

## Add dependency

```shell
pipenv install --dev some-what-module
```

# How to release

Create new release on Github, then Github Actions automatically uploads the
module to PyPI.

## How to update launchable/jar/exe_deploy.jar

```
bazel build //src/main/java/com/launchableinc/ingest/commits:exe_deploy.jar
cp bazel-bin/src/main/java/com/launchableinc/ingest/commits/exe_deploy.jar launchable/jar/exe_deploy.jar
 ```

# Installing CLI

You can install the `launchable` command from either source or [pypi](https://pypi.org/project/launchable/).

## Prerequisite

- \>= Python 3.5
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
