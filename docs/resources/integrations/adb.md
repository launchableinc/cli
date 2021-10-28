---
description: >-
  This page outlines how the Launchable CLI interfaces with Android Debug Bridge
  (adb).
---

# Android Debug Bridge (adb)

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

Currently, the CLI doesn't have a `record tests` command for ADB. Use the [Gradle command](gradle.md#recording-test-results) instead.

## Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of tests/test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
# '-e log true' option outputs test names without running
adb shell am instrument \
  -w \
  -r \
  -e log true \
  -e debug false \
  com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner \
  > test_list.txt
cat test_list.txt | \
  launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  adb > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
adb shell am instrument -w -e class $(cat launchable-subset.txt) com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner
```
