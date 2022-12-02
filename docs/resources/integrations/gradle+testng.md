---
description: This page outlines how the Launchable CLI interfaces with Gradle+TestNG.
---

# Gradle+TestNG

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started.md), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/) for more comprehensive usage guidelines.
{% endhint %}

{% hint style="info" %}
This page is for users who use Gradle and TestNG to write tests. If you are not using TestNG, refer to [another page](gradle.md)
{% endhint %}

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> gradle ./build/test-results/test/
```

* By default, Gradle's report files are saved to `build/test-results/test/`, but that might be different depending on how your Gradle project is configured.
* You can specify multiple directories if you do multi-project build.
* For a large project, a dedicated Gradle task to list up all report directories might be convenient. See [the upstream documentation](https://docs.gradle.org/current/userguide/java\_testing.html#test\_reporting) for more details and insights.
* Alternatively, you can specify a glob pattern for directories or individual test report files (this pattern might already be specified in your pipeline script for easy copy-pasting), e.g. `gradle **/build/**/TEST-*.xml`.

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

First, you need to add a dependency declaration to `build.gradle` so that the right subset of tests get executed when TestNG runs:

```
dependencies {
    ...
    testRuntime 'com.launchableinc:launchable-testng:1.0.0'
}
```

The high level flow for subsetting is:

1. Get the full list of test directories/tests/test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the directories containing tests you would normally run (e.g. `project1/src/test/java`) and pass that to `launchable subset`:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  gradle \
  --bare \
  project1/src/test/java \
  project2/src/test/java > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Choosing a subset optimization target](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/choosing-a-subset-optimization-target/) for more info.

This creates a file called `launchable-subset.txt`. For Gradle, this file is formatted like:

```
MyTestClass1
MyTestClass2
...
```

You can pass this file into the Gradle launchable extension through an environment variable:

```bash
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
gradle test
```

Note: The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
./gradlew testDebugUnitTest
# or
./gradlew testReleaseUnitTest
```
