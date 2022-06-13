---
description: This page outlines how the Launchable CLI interfaces with pytest.
---

# pytest

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
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
[Same as the CLI](https://docs.launchableinc.com/getting-started).

### Generate a config file
`launchable-config` is a command-line tool to generate and validate configuration files.

```bash
# via pipenv
pipenv run launchable-config --create

# via pip
launchable-config --create
```

A template `.launchable.d/config.yml` file is generated in the current directory in YAML format.

### Verify a config file

```bash
# via pipenv
pipenv run launchable-config --verify

# via pip
launchable-config --verify
```

Verify the contents of the `.launchable.d/config.yml` file. If you have problems, edit the file accordingly.

### Configure your pytest command with the plugin

`pytest-launchable` is a plugin for pytest; based on the config file created by launchable-config, it runs the pytest test while using Launchable and records the results.

Just add an `--launchable` option to the pytest command. It is very easy.

```bash
pytest --launchable <your-pytest-project>
```

If the configuration file is not in the current directory, use `--launchable-conf-path` option.

```bash
pytest --launchable --launchable-conf-path <path-to-launchable-configuration-file> <your-pytest-project>
```

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
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../features/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
pytest --junit-xml=test-results/subset.xml $(cat launchable-subset.txt)
```
