# Subsetting your test runs

## Requesting and running a subset

Subsetting instructions depend on the test runner or build tool you use to run tests. Click the appropriate link below to get started:

* [Android Debug Bridge \(ADB\)](test-runners/adb.md#subsetting-your-test-runs)
* [Ant](test-runners/ant.md#subsetting-your-test-runs)
* [Bazel](test-runners/bazel.md#subsetting-your-test-runs)
* [Behave](test-runners/behave.md#subsetting-your-test-runs)
* [CTest](test-runners/ctest.md#subsetting-your-test-runs)
* [Cypress](test-runners/cypress.md#subsetting-your-test-runs)
* [GoogleTest](test-runners/googletest.md#subsetting-your-test-runs)
* [Go Test](test-runners/go-test.md#subsetting-your-test-runs)
* [Gradle](test-runners/gradle.md#subsetting-your-test-runs)
* [Maven](test-runners/maven.md#subsetting-your-test-runs)
* [Minitest](test-runners/minitest.md#subsetting-your-test-runs)
* [Nose](test-runners/nose.md#subsetting-your-test-runs)
* [Robot](test-runners/robot.md#subsetting-your-test-runs)
* [RSpec](test-runners/rspec.md#subsetting-your-test-runs)

## Other tips

### "Training wheels" mode with the --rest option

You can start subsetting by just splitting your existing suite into an intelligent subset and then the rest of the tests. After you've dialed in the right subset target, you can then remove the remainder and run the full suite less frequently. See the diagram below for a visual explanation.

![](.gitbook/assets/shift-right.png)

The middle row of the diagram shows how you can start by splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

The example below shows how you can generate a subset \(`launchable-subset.txt`\) and the remainder \(`launchable-remainder.txt`\) using the `--rest` option. Here we're using Ruby and Minitest:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  minitest test/**/*.rb > launchable-subset.txt
```

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` that you can pass into your command to run tests in two stages. Again, using Ruby as an example:

```bash
bundle exec rails test $(cat launchable-subset.txt)

bundle exec rails test $(cat launchable-remainder.txt)
```

You can remove the second part after you're happy with the results. Once you do this, make sure to continue running the full test suite at some stage as described in [Preparing your pipeline](subsetting-your-test-runs.md#preparing-your-pipeline).

