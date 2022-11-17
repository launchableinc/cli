---
description: This page outlines how the Launchable CLI interfaces with Gradle.
---

# Gradle

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started.md), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/) for more comprehensive usage guidelines.
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

{% hint style="info" %}
For instructions on how to implement [Zero Input Subsetting](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting.md), scroll down to [Using Zero Input Subsetting](#using-zero-input-subsetting).
{% endhint %}

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
  project1/src/test/java \
  project2/src/test/java > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Choosing a subset optimization target](../../features/predictive-test-selection/choosing-a-subset-optimization-target.md) for more info.

This creates a file called `launchable-subset.txt`. For Gradle, this file is formatted like:

```
--tests MyTestClass1 --tests MyTestClass2 ...
```

You can pass this into your command to run only the subset of tests:

```bash
gradle test $(cat launchable-subset.txt)
# equivalent to gradle test --tests MyTestClass1 --tests MyTestClass2 ...
```

Note: The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
./gradlew testDebugUnitTest $(cat launchable-subset.txt)
# or
./gradlew testReleaseUnitTest $(cat launchable-subset.txt)
```

### Using Zero Input Subsetting

To use [Zero Input Subsetting](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting.md), follow these instructions.

First, you need to add a snippet to your Gradle config to enable test exclusion via the Gradle command line:

```
test {
    if (project.hasProperty('excludeTests')) {
        exclude project.property('excludeTests').split(',')
    }
}
```

Then, to retrieve a list of non-prioritized tests (per [Zero Input Subsetting](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting.md)), run:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \ # or another optimization target
  --get-tests-from-previous-sessions \
  --output-exclusion-rules \
  gradle . > launchable-exclusion-list.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Choosing a subset optimization target](../../features/predictive-test-selection/choosing-a-subset-optimization-target.md) for more info.

This creates a file called `launchable-exclusion-list.txt`. For Gradle, this file is formatted like:

```
-PexcludeTests=com/example/FooTest.class,com/example/BarTest.class
```

You can pass this into your command to exclude the non-prioritized tests. This will make sure only prioritized and new tests are run:

```bash
gradle test $(cat launchable-exclusion-list.txt)
# equivalent to gradle test -PexcludeTests=com/example/FooTest.class,com/example/BarTest.class
```

Note: The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
./gradlew testDebugUnitTest $(cat launchable-exclusion-list.txt)
# or
./gradlew testReleaseUnitTest $(cat launchable-exclusion-list.txt)
```

### Bare output

By default, the CLI outputs a list of classes each with a prefix (`--tests ` or `-PexcludeTests=` depending on the above). However, in some cases, a raw list of class names is preferable. Use the `--bare` option to enable this formatting. Note that this option goes **after** the `gradle` string:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \ # or another optimization target
  gradle \
  --bare \
  . > subset.txt
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
        working-directory: ./
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      # You need JDK 1.8.
      - name: Set up JDK 1.8
        uses: actions/setup-java@v1
        with:
          java-version: 1.8
      - name: Run test
        run: |
          # Install launchable CLI.
          python -m pip install --upgrade pip
          pip install wheel setuptools_scm
          pip install launchable

          # Verify launchable command.
          launchable verify

          # Record build name.
          launchable record build --name ${{ github.sha }} --source src=.

          # Subset tests up to 80% of whole tests.
          launchable subset --target 80% --build ${{ github.sha }} gradle src/test/java > subset.txt

          # Run subset test and export the result to report.xml.
          gradle test $(cat subset.txt)

          # Record test result.
          launchable record tests --build ${{ github.sha }} gradle ./build/test-results/test
```
