
This page outlines how the Launchable CLI interfaces with $RUNNER.

{% hint style="info" %}
This is a reference page. See [Getting started](../getting-started.md), [Sending data to Launchable](../sending-data-to-launchable.md), and [Subsetting your test runs](../subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

# Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
5
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../resources/always-run.md).
{% endhint %}

# Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of tests/test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
1
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
2
```