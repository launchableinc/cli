# Recording builds from multiple repositories

## Multiple repositories combined in one build then tested

If you produce a build by combining code from several repositories (like the diagram below), invoke `launchable record build` with multiple `--source` options to denote them.

![Software built from two repositories and then tested](<../.gitbook/assets/Recording from multiple repos@2x (2).png>)

To differentiate them, provide a label for each repository in the form of `LABEL=PATH`:

```bash
# record the build
launchable record build --name <BUILD NAME> --source main=./main_repo --source lib=./lib_repo

# create the build
bundle install
```

{% hint style="info" %}
Note: `record build` automatically recognizes [Git submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), so there’s no need to explicitly declare them.
{% endhint %}

## Multiple repositories built/deployed separately then tested together (e.g. microservices)

Some teams run regression tests against an environment where several services have been deployed. Each service is built from code from its own repository (or set of repositories), as shown in the diagram below.

![Several microservices built, deployed, and tested together](<../.gitbook/assets/Recording from multiple repos@2x.png>)

The intent of recording a build is to capture the version of the software being tested. In _this_ scenario, the version of the software being tested is effectively the combination of all versions of the components deployed to the test environment.

For example, if the currently deployed version of service 1 is `d7bf8b7c` (from repo 1) and the currently deployed version of service 2 is `c39b86a1` (from repo 2), then the effective version of the software being tested can be thought of as something like:

```json
[
  {
    repository: "repo1",
    commit: "d7bf8b7c"
  },
  {
    repository: "repo2",
    commit: "c39b86a1"
  }
]
```

This mental model is no different than [the example above](recording-builds-from-multiple-repositories.md#multiple-repositories-combined-in-one-build-then-tested). However, because you want to capture the versions of all of the deployed software being tested, you need to run `launchable record build` right before running tests — i.e. in the green box in the diagram above.

This presents a challenge because the repos for each service are _usually_ not available at this stage (and cloning them just for this purpose would be inefficient). Luckily, when you run `launchable record build`, the CLI actually performs two functions that we can split up to support this use case:

1. Recording all new commits from included repositories, and
2. Recording the build itself, 'tagged' with the HEAD commit from each included repository

The CLI provides options to separate these: you can record commits in each component's build process and then record the "combined" build itself right before you run tests.&#x20;

The commands and options that enable this are:

1. `launchable record commit --source REPO=/PATH/TO/REPO` , which lets you record commits separately in each component's build process, and
2. Two `launchable record build` options:
   1. `--no-commit-collection` which disables commit collection (since you're doing it separately), and
   2. `--commit REPO=HASH` which lets you 'tag' the build with each repository\
      _(Note: This means that the deployed version of each service needs to be available to the process where you run tests.)_

These commands and steps are shown in the white boxes in the expanded diagram below.

![Launchable commands to collect data from several microservices built, deployed, and tested together](<../.gitbook/assets/Recording from multiple repos@2x (3).png>)

