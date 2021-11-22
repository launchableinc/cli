---
description: This page outlines how the Launchable CLI interfaces with cucumber.
---

# Cucumber

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

First, use the [junit report plugin](https://cucumber.io/docs/cucumber/reporting/) to create test reports:

```bash
bundle exec cucumber -f junit -o reports
```

After running tests, point the CLI to your test report files to collect test results and train the model:

```
launchable record tests --build <BUILD NAME> cucumber ./reports/**/*.xml
```

If you receive a warning messages such as `Cannot find test file Test-feature-example.xml`, set the project's root directory path with the `--base` option:

```
launchable record tests --build <BUILD NAME> --base /example/project cucumber /example/project/reports/**/*.xml
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of tests/test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run (with `features/**/*.feature`) and pass that to `launchable subset`:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  cucumber features/**/*.feature > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
bundle exec cucumber $(cat launchable-subset.txt)
```
