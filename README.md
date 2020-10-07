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
launchable record commit
```

### Collect build

```shell
launchable record build --name BUILD_ID --source REPO_DIST
```

#### Example
```shell
launchable record build --name 12345678 --source .
```

`--source` can be specified multiple.
```shell
launchable record build --name 12345678 --source . --source modules/submodule_a
```

# Development
You can use Python's `-m` option to launch module directly.
```shell
python -m launchable.cli record collect
```