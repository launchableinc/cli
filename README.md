# Installation

```shell
pip install launchable
```

## Set your API token

```shell
export LAUNCHABLE_TOKEN=set_your_token
```

# How to use
## Basic usage
### Collect build and commit

```shell
launchable record build --name BUILD_ID --source name=REPO_DIST
```

#### Example
```shell
launchable record build --name 12345678 --source main=.
```

## Optional
### Collect commit

```shell
launchable record commit --source .
```

# Development
You can use Python's `-m` option to launch module directly.
```shell
python3 -m launchable record commit
```
