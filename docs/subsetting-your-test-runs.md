# Subsetting your test runs

## Overview

TODO: Explain value prop

The high level flow for subsetting is:

1. Get the full list of tests/test paths and pass that to `launchable subset` with:
   1. an optimization target for the subset
   2. a build name, so Launchable can choose the best tests for the changes in the build
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

The diagram below illustrates the interactions between your tools, the Launchable CLI, and the Launchable platform:

![](.gitbook/assets/subsetting-diagram.png)

{% hint style="info" %}
The diagram above uses the generic term test _files_, but the real object type may be different depending on your stack \(e.g. test _classes_, test _targets_, etc.\).
{% endhint %}

## Preparing your pipeline

Adding a new step to your pipeline if necessary:

* Shift left: a new pipeline to run the subset \(if you don't have one already\)
* Shift right: a new pipeline to run all the tests \(if you don't have one already\)

## Choosing an optimization target

* Explain confidence curves and comprehensiveness curves \(even though it's not in the webapp yet\)
  * What each one measures
  * When you would want to use one over the other
* Explain target options
  * Confidence target
  * Fixed duration target
  * % duration target

## Requesting and running a subset

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`. Here's an example using Ruby and Minitest:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  minitest test/**/*.rb > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

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

You can remove the second part after you're happy with the results. Once you do this, make sure to continue running the full test suite at some stage as described in [Preparing your pipeline](https://github.com/launchableinc/cli/tree/23db81ebf60588ba00bb9c0f059795ad7e93f289/docs/subsetting-your-tests.md#preparing-your-pipeline).

