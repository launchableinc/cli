# Minitest \(Ruby\)

## Getting started

First, follow the steps in the [Getting started](../getting-started.md) guide to install the Launchable CLI, set your API key, and verify your connection.

Then return to this page to complete the integration.

## Recording builds

Launchable chooses which tests to run based on the changes contained in a **build**. To enable this, you need to send build information to Launchable.

Right before you create a build in your CI script, invoke the Launchable CLI as follows:

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`.

## Subsetting tests

To select meaningful subset of tests, feed all test Ruby source files to Launchable, like this:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  minitest test/**/*.rb > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with.

This command creates a `launchable-subset.txt` file that contains the subset of tests that should be run. You can now invoke minitest to run exactly those tests:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

## Recording test results

First, minitest has to be configured to produce JUnit compatible report files. We recommend [minitest-ci](https://github.com/circleci/minitest-ci).

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
bundle exec rails test

launchable record tests --build <BUILD NAME> minitest "$CIRCLE_TEST_REPORTS/reports"
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests minitest --help`