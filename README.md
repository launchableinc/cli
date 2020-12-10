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

## Docker

You can get DockerImage from docker hub.
https://hub.docker.com/repository/docker/launchableinc/cli

```sh
$ docker pull launchableinc/ingester:latest
$ docker run -it -e LAUNCHABLE_TOKEN=v1:launchableinc/reponame:xxxxx launchableinc/cli:latest launchable verify
Platform: Linux-5.4.39-linuxkit-x86_64-with-debian-10.5
Python version: 3.7.3
Java command: java
Your CLI configuration is successfully verified 🎉
```

You can easily integrate it into your CircleCI jobs.

```
launchable_verify:
  docker:
    - image: launchableinc/cli:latest
      environment:
        LAUNCHABLE_TOKEN: $LAUNCHABLE_TOKEN
  steps:
    - run:
        name: launchable verify?
        command: launchable verify || true
```
