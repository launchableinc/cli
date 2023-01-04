---
description: This page outlines how the Launchable interfaces with pytest.
---

# pytest

{% hint style="info" %}
This is a reference page. See [Getting started](../../sending-data-to-launchable/using-the-launchable-cli/getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/) for more comprehensive usage guidelines.
{% endhint %}

Launchable interfaces with pytest via

1. the Launchable pytest plugin
2. the Launchable CLI

## Launchable pytest plugin

We offer a new way to integrate Launchable, a native pytest plugin.

### Installing the plugin

The Launchable pytest plugin is a Python3 package that you can install from [PyPI](https://pypi.org/project/pytest-launchable/).

{% hint style="warning" %}
The plugin requires **Python 3.7+**, **Pytest 4.2.0+**, _and_ **Java 8+**.
{% endhint %}

If you use Pipenv, you can install the plugin into your repository:

```bash
pipenv install --dev pytest-launchable
```

Or, you can install the CLI in your CI pipeline by adding this to the part of your CI script where you install dependencies:

```bash
pip3 install pytest-launchable
```

You don't need to install Lanchable CLI separately because the plugin automatically installs the CLI and uses it internally.

### Setting your API key

First, create an API key for your workspace at [app.launchableinc.com](https://app.launchableinc.com). This authentication token allows the pytest plugin to talk to Launchable.

Then, make this API key available as the `LAUNCHABLE_TOKEN` environment variable in your CI process. How you do this depends on your CI system:

| CI system              | Docs                                                                                                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure DevOps Pipelines | [Set secret variables](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops\&tabs=yaml%2Cbatch#secret-variables)                                              |
| Bitbucket Pipelines    | [Variables and secrets](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)                                                                                                   |
| CircleCI               | [Using Environment Variables](https://circleci.com/docs/2.0/env-vars/)                                                                                                                               |
| GitHub Actions         | [How to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets)                                                                                     |
| GitLab CI              | [GitLab CI/CD environment variables](https://docs.gitlab.com/ee/ci/variables/)                                                                                                                       |
| GoCD                   | [Setting variables on an environment](https://docs.gocd.org/current/faq/dev\_use\_current\_revision\_in\_build.html#setting-variables-on-an-environment)                                             |
| Jenkins                | <p><a href="https://docs.cloudbees.com/docs/cloudbees-ci/latest/cloud-secure-guide/injecting-secrets">Injecting secrets into builds</a></p><p>(Create a global "secret text" to use in your job)</p> |
| Travis CI              | [Environment Variables](https://docs.travis-ci.com/user/environment-variables/)                                                                                                                      |

### Generate a config file

`launchable-config` is a command-line tool to generate and validate configuration files. The Launchable pytest plugin uses this config.

First, generate a new config file:

```bash
# via pipenv
pipenv run launchable-config --create

# via pip
launchable-config --create
```

This generates a template `.launchable.d/config.yml` file in the current directory that looks like this:

```yml
# Launchable test session configuration file
# See https://docs.launchableinc.com/resources/cli-reference for detailed usage of these options
#  
schema-version: 1.0
build-name: commit_hash
record-build:
  # Put your git repository location here
  source: .
  max_days: 30
record-session:
subset:
  # mode is subset, subset-and-rest, or record-only
  mode: subset
  # you must specify one of target/confidence/time
  # examples:
  #   target: 30%  # Create a variable time-based subset of the given percentage. (0%-100%)
  #   confidence: 30%  # Create a confidence-based subset of the given percentage. (0%-100%)
  #   time: 30m  # Create a fixed time-based subset. Select the best set of tests that run within the given time bound. (e.g. 10m for 10 minutes, 2h30m for 2.5 hours, 1w3d for 7+3=10 days. )
  target: 30%
record-tests:
  # The test results are placed here in JUnit XML format
  result_dir: launchable-test-result
```

You can then edit the config file per the directions below.

### Recording test results (pytest plugin)

#### Update your config file

In `.launchable.d/config.yml`:

1. Check that the `source` option in the `record-build` section points to your Git repository (the default is `.`, the current directory).
2. Check that the `mode` option in the `subset` section is set to `record-only`

#### Verify your config file

Verify the contents of the `.launchable.d/config.yml` file:

```bash
# via pipenv
pipenv run launchable-config --verify

# via pip
launchable-config --verify
```

If any problems are reported, edit the file accordingly.

#### Use the plugin with pytest

Then, just add an `--launchable` option to the pytest command. It is very easy:

```bash
pytest --launchable <your-pytest-project>
```

If the configuration file is not in the current directory, use the `--launchable-conf-path` option:

```bash
pytest --launchable --launchable-conf-path <path-to-launchable-configuration-file> <your-pytest-project>
```

This will:

1. Create a build in your Launchable workspace
2. Run your tests
3. Submit your test reports to Launchable
4. Leave XML reports in the `launchable-test-result` by default

### Requesting and running a subset of tests

#### Update your config file

In `.launchable.d/config.yml`:

1. Check that the `source` option in the `record-build` section points to your Git repository (the default is `.`, the current directory).
2. Check that the `mode` option in the `subset` section is set to `subset` or `subset_and_rest` [based on your needs](../../features/predictive-test-selection/#training-wheels-mode-with-the-rest-option)
3. Check that one of the three [optimization target options](../../features/predictive-test-selection/#choosing-an-optimization-target) are set (`target`, `confidence`, or `time`)

#### Verify your config file

Verify the contents of the `.launchable.d/config.yml` file:

```bash
# via pipenv
pipenv run launchable-config --verify

# via pip
launchable-config --verify
```

If any problems are reported, edit the file accordingly.

#### Use the plugin with pytest

Then, just add an `--launchable` option to the pytest command. It is very easy:

```bash
pytest --launchable <your-pytest-project>
```

If the configuration file is not in the current directory, use the `--launchable-conf-path` option:

```bash
pytest --launchable --launchable-conf-path <path-to-launchable-configuration-file> <your-pytest-project>
```

This will:

1. Create a build in your Launchable workspace
2. Request a subset of tests based on your optimization target
3. Run those tests (or run all the tests if `subset_and_rest` mode is chosen)
4. Submit your test reports to Launchable
5. Leave XML reports in the `launchable-test-result` by default

## Launchable CLI

See [recording-test-results-with-the-launchable-cli](../../sending-data-to-launchable/using-the-launchable-cli/recording-test-results-with-the-launchable-cli/ "mention") and [subsetting-with-the-launchable-cli](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/ "mention") for more information.
