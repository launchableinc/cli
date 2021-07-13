---
description: This page outlines how the Launchable CLI interfaces with Gradle.
---

# Gradle

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> gradle ./build/test-results/test/
```

* By default, Gradle's report files are saved to `build/test-results/test/`, but that might be different depending on how your Gradle project is configured.
* You can specify multiple directories if you do multi-project build.
* For a large project, a dedicated Gradle task to list up all report directories might be convenient. See [the upstream documentation](https://docs.gradle.org/current/userguide/java_testing.html#test_reporting) for more details and insights.
* Alternatively, you can specify a glob pattern for directories or individual test report files \(this pattern might already be specified in your pipeline script for easy copy-pasting\), e.g. `gradle **/build/**/TEST-*.xml`.

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
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  gradle project1/src/test/java project2/src/test/java > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
gradle test $(cat launchable-subset.txt)
```

Note: The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
./gradlew testDebugUnitTest $(cat launchable-subset.txt)
```

Or:

```bash
./gradlew testReleaseUnitTest $(cat launchable-subset.txt)
```

