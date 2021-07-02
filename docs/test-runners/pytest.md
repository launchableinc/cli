# Pytest

This page outlines how the Launchable CLI interfaces with Pytest.

{% hint style="info" %}
This is a reference page. See [Getting started](../getting-started.md), [Sending data to Launchable](../sending-data-to-launchable.md), and [Subsetting your test runs](../subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

# Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> pytest ./test-results/
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../resources/always-run.md).
{% endhint %}

* You can specify multiple directories if you do multi-project build:

## Subset your test runs

Subsetting instructions differ depending on whether you plan to [shift tests left](../#shift-left) or [shift tests right](../#shift-right):

### Shift left

First, set up a new test execution job/step/pipeline to run earlier in your software development lifecyle.

Then, to retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  pytest tests > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
pytest --junit-xml=test-results/subset.xml $(cat launchable-subset.txt)
```

Make sure to continue running the full test suite at some stage. Run `launchable record build` and `launchable record tests` for those runs to continually train the model.

### Shift right

The [shift right](../#shift-right) diagram suggests first splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

To retrieve a subset of tests, first pass the full list of test candidates to `launchable subset`. For example:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  pytest tests > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.
* The `--rest` option writes all the other tests to a file so you can run them separately.

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` that you can pass into your command to run tests in two stages:

```bash
pytest --junit-xml=test-results/subset.xml $(cat launchable-subset.txt)

pytest --junit-xml=test-results/remainder.xml $(cat launchable-remainder.txt)
```

You can remove the second part after we've let you know that the model is sufficiently trained. Once you do this, make sure to continue running the full test suite at some stage. Run `launchable record build` and `launchable record tests` for those runs to continually train the model.

