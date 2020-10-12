# Installation

```shell
pip install launchable
```

## Set your API token

```shell
export LAUNCHABLE_TOKEN=set_your_token
```

# How to use

### Collect commit

```shell
launchable record commit --source .
```

### Collect build

```shell
launchable record build --name BUILD_ID --source REPO_DIST
```

#### Example
```shell
launchable record build --name 12345678 --source main=.
```

`--source` can be specified multiple.
```shell
launchable record build --name 12345678 --source main=. --source sub1=modules/submodule_a
```

# Development
You can use Python's `-m` option to launch module directly.
```shell
python3 -m launchable record commit
```
