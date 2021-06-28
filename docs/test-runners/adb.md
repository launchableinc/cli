# Android Debug Bridge \(ADB\)

{% hint style="info" %}
Hey there, did you land here from search? FYI, Launchable helps teams test faster, push more commits, and ship more often without sacrificing quality \([here's how](https://www.launchableinc.com/how-it-works)\). [Sign up](https://app.launchableinc.com/signup) for a free trial for your team, then read on to see how to add Launchable to your testing pipeline.
{% endhint %}

## Getting started

First, follow the steps in the [Getting started](../getting-started.md) guide to install the Launchable CLI, set your API key, and verify your connection.

Then return to this page to complete the three steps of implementation:

1. Recording builds
2. Recording test results
3. Subsetting test execution

## Recording builds

Launchable selects tests based on the changes contained in a **build**. To send metadata about changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`. See [Data privacy and protection](../security/data-privacy-and-protection.md) for more info.

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
  --target <TARGET> \
  adb > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
adb shell am instrument -w -e class $(cat launchable-subset.txt) com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner
```
