---
description: This page outlines how the Launchable CLI interfaces with pytest.
---

# pytest

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started.md), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/) for more comprehensive usage guidelines.
{% endhint %}

## Native pytest plugin

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

### Subsetting your test runs (pytest plugin)

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

## Legacy CLI profile

### Recording test results

When you run tests, create a JUnit XML test report using the `--junit-xml` option, e.g.:

```
pytest --junit-xml=test-results/results.xml
```

{% hint style="warning" %}
If you are using pytest 6 or later, please specify `junit_family=legacy` as the report format. pytest has changed its default test report format from `xunit1` to `xunit2` since version 6. See [Deprecations and Removals — pytest documentation](https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2). The `xunit2` format does not output the file name in the report, and the file name is required to use Launchable.
{% endhint %}

Then, after running tests, point the CLI to your test report file(s) to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> pytest ./test-results/
```

#### --json option

When you produce report files used by [pytest-dev/pytest-reportlog](https://github.com/pytest-dev/pytest-reportlog) plugin, you can use `--json` option.

```
pytest --report-log=test-results/results.json
launchable record tests --build <BUILD NAME> pytest --json ./tests-results/
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

### Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
 pytest --collect-only  -q | launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  pytest > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../features/predictive-test-selection/) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
pytest --junit-xml=test-results/subset.xml $(cat launchable-subset.txt)
```

## Example integration to your CI/CD

### GitHub Actions
You can easily integrate to your GitHub Actions pipeline.

```yaml
name: gradle-test-example

on:
  push:
    branches: [main]

env:
  LAUNCHABLE_TOKEN: ${{ secrets.LAUNCHABLE_TOKEN }}
  LAUNCHABLE_DEBUG: 1
  LAUNCHABLE_REPORT_ERROR: 1

jobs:
  tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: python
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      # You need JDK 1.8.
      - name: Set up JDK 1.8
        uses: actions/setup-java@v1
        with:
          java-version: 1.8
      - name: Install CLI
        run: |
          # Install launchable CLI.
          python -m pip install --upgrade pip
          pip install wheel setuptools_scm
          pip install launchable
      # Verify launchable command.
      - name: Verify launchable CLI
        run: launchable verify
      # Record build name.
      - name: Record build name
        run: launchable record build --name ${{ github.sha }} --source src=.
      # Subset tests up to 80% of whole test and run test.
      - name: Verify launchable CLI
        run: |
          launchable subset --target 80% --build ${{ github.sha }} pytest . > subset.txt
          # Run subset test and export the result to report.xml.
          pytest --junitxml=./report/report.xml $(cat subset.txt)
      # Record test result.
      - name: Record test result
        run: launchable record tests --build ${{ github.sha }} pytest ./report/
        if: always()
```
