# Installation

```shell
pip3 install --user launchable
```

This creates executable `~/.local/bin/launchable` that should be on your `PATH`. See [PEP-370](https://www.python.org/dev/peps/pep-0370/) for further details.

## Set your API token

```shell
export LAUNCHABLE_TOKEN=set_your_token
```

# How to use
## Basic usage
### Record build and commit

Basic usage,

```shell
launchable record build --name BUILD_ID --source .
```

Or if you want to specify the repo name,

```shell
launchable record build --name BUILD_ID --source REPO_NAME=REPO_DIST
```

#### Example
```shell
launchable record build --name 12345678 --source main=.
```

## Optional
### Separate commit recording

Basically, `launchable record build` record commit data simultaneously. If you want to record commit individually, you could separate recording commit and build.

Using `launchable record build --without-commit` , the command surpress commit recoding.

```shell
launchable record build --name 12345678 --source main=. --without-commit
```

To record commit individually, use `record commit`.

```shell
launchable record commit --source .
```
