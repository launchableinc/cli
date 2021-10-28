---
description: >-
  This page outlines how the Launchable CLI interfaces with the NUnit console
  runner.
---

# NUnit

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

Launchable CLI parses [the NUnit3 style test report XML files](https://docs.nunit.org/articles/nunit/technical-notes/usage/XML-Formats.html) produced from NUnit.

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> nunit path/to/TestResult.xml
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of tests/test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
nunit3-console --explore=list.xml path/to/myassembly.dll
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  nunit list.xml > launchable-subset.txt
```

{% hint style="warning" %}
If you pass any additional filters to `nunit-3-console` when you _run_ tests, make sure to pass those same filters when you run `nunit3-console --explore...`. This ensures that the same list of tests that you planned to run gets passed to Launchable for prioritization.
{% endhint %}

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
nunit3-console --testlist=launchable-subset.txt path/to/myassembly.dll
```
