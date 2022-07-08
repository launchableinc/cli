# Subsetting your test runs

## Overview

Soon after you've started sending data, you can start using Launchable to subset your test runs and save time.

The high level flow for subsetting is:

1. Get the full list of tests (or test files, targets, etc.) and pass that to `launchable subset` along with:
   1. an optimization target for the subset
   2. a build name, so Launchable can choose the best tests for the changes in the build being tested
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

The diagram below illustrates the interactions between your tools, the Launchable CLI, and the Launchable platform:

![](../../.gitbook/assets/subsetting-diagram.png)

{% hint style="info" %}
The diagram above uses the generic term test _files_, but the real object type may be different depending on your stack (e.g. test _classes_, test _targets_, etc.).
{% endhint %}

## Preparing your pipeline for subsetting

Depending on your goal, you might need to make a few changes to your pipeline to adopt subsetting.

### Goal: Run a subset of tests at the same stage of your software delivery lifecycle

After subsetting your tests, you should make sure to run the full suite of tests at _some point_ later in your pipeline.

For example, once you start running a subset of an integration test suite that runs on pull requests, you should make sure to run the **full** integration test suite after a PR is merged (and record the outcome of those runs with `launchable record tests`).

![Run the full suite after merging](../../.gitbook/assets/shift-right-simple.png)

### Goal: Run a subset of tests earlier in your software delivery lifecycle ("shift left")

If your goal is to run a short subset of a long test suite earlier in the development process, then you may need to set up a new pipeline to run tests in that development phase. For example, if you currently run a long nightly test suite, and you want to run a subset of that suite every hour, you may need to create a pipeline to build, deploy, and run the subset if one doesn't exist already.

You'll also want to continue running the full test suite every night (and recording the outcome of those runs with `launchable record tests`).

![Shift nightly tests left](../../.gitbook/assets/shift-left-new.png)

## Choosing an optimization target

The optimization target you choose determines how Launchable populates a subset with tests. You can use the **Confidence** **curve** shown on the Simulate page in the Launchable dashboard to choose an optimization target.

![](<../../.gitbook/assets/app.launchableinc.com\_organizations\_demo\_workspaces\_demo\_actions\_predictive-test-selection (1).png>)

### Confidence target (`--confidence`)

{% hint style="info" %}
The confidence target is designed for use with test suites where the list of tests in each [test-session.md](../../concepts/test-session.md "mention") used to train your model is the same each time.

If your sessions have variable test lists, use the percentage time target instead.
{% endhint %}

**Confidence** is shown on the y-axis of a confidence curve. When you request a subset using `--confidence 90%`, Launchable will populate the subset with relevant tests up to the corresponding expected duration value on the x-axis. For example, if the corresponding duration value for 90% confidence is 3 minutes, Launchable will populate the subset with up to 3 minutes of the most relevant tests for the changes in that build. This is useful to start with because the duration should decrease over time as Launchable learns more about your changes and tests.

{% hint style="warning" %}
It's possible for all tests to be returned in a subset request when you use `--confidence`.&#x20;

For example, let's say you request a subset with a 90% confidence target, which corresponds to 30 minutes of tests on the X-axis of your workspace's confidence curve. If the total estimated duration of the request's [#input-test-list](../../concepts/subset.md#input-test-list "mention") is less than 30 minutes, then all of the input tests will be returned in the subset.

This is why the confidence target should only be used with test suites that have consistent test lists.
{% endhint %}

### Fixed time target (`--time`)

{% hint style="info" %}
The fixed time target is designed for use with test suites where the total duration of each run used to train the model is relatively stable. If your runs have highly variable duration, the percentage time target may be more useful.
{% endhint %}

**Time** is shown on the x-axis of a confidence curve. When you request a subset using `--time 10m`, Launchable will populate the subset with up to 10 minutes of the most relevant tests for the changes in that build. This is useful if you have a maximum test runtime in mind.

{% hint style="warning" %}
It's possible for all tests to be returned in a subset request when you use `--time`.&#x20;

For example, let's say you request a subset with a time target of 30 minutes. If the total estimated duration of the request's [#input-test-list](../../concepts/subset.md#input-test-list "mention") is less than 30 minutes, then all of the input tests will be returned in the subset.

This is why the time target should only be used with test suites that have consistent test lists.
{% endhint %}

### Percentage time target (`--target`)

{% hint style="info" %}
**Percentage time** is not yet shown in the Launchable dashboard.
{% endhint %}

When you request a subset using `--target 20%`, Launchable will populate the subset with 20% of the expected duration of the most relevant tests. For example, if the expected duration of the full list of tests passed to `launchable subset` is 100 minutes, Launchable will return up to 20 minutes of the most relevant tests for the changes in that build.

This is useful if your test sessions vary in duration.

## Requesting and running a subset

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`. Here's an example using Ruby/minitest and `--confidence`:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence 90% \
  minitest test/**/*.rb > launchable-subset.txt
```

The `--build` option should use the same `<BUILD NAME>` value that you used in `launchable record build`.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

Subsetting instructions depend on the test runner or build tool you use to run tests. Click the appropriate link below to get started:

* [Android Debug Bridge (adb)](../../resources/integrations/adb.md#subsetting-your-test-runs)
* [Ant](../../resources/integrations/ant.md#subsetting-your-test-runs)
* [Bazel](../../resources/integrations/bazel.md#subsetting-your-test-runs)
* [Behave](../../resources/integrations/behave.md#subsetting-your-test-runs)
* [CTest](../../resources/integrations/ctest.md#subsetting-your-test-runs)
* [Cypress](../../resources/integrations/cypress.md#subsetting-your-test-runs)
* [GoogleTest](../../resources/integrations/googletest.md#subsetting-your-test-runs)
* [Go Test](../../resources/integrations/go-test.md#subsetting-your-test-runs)
* [Gradle](../../resources/integrations/gradle.md#subsetting-your-test-runs)
* [Jest](../../actions/resources/supported-languages/jest.md#subsetting-your-test-runs)
* [Maven](../../resources/integrations/maven.md#subsetting-your-test-runs)
* [minitest](../../resources/integrations/minitest.md#subsetting-your-test-runs)
* [nose](../../resources/integrations/nose.md#subsetting-your-test-runs)
* [pytest](../../resources/integrations/pytest.md#subsetting-your-test-runs-pytest-plugin)
* [Robot](../../resources/integrations/robot.md#subsetting-your-test-runs)
* [RSpec](../../resources/integrations/rspec.md#subsetting-your-test-runs)

{% hint style="info" %}
If you're not using any of these, use the [generic 'file-based' runner integration](../../resources/integrations/using-the-generic-file-based-runner-integration.md), the [`raw` profile for custom test runners](../../resources/integrations/raw.md), or [request a plugin](mailto:support@launchableinc.com?subject=Request%20a%20plugin).
{% endhint %}

### Inspecting subset details

You can use `launchable inspect subset` to inspect the details of a specific subset, including rank and expected duration. This is useful for verifying that you passed the correct tests or test directory path(s) into `launchable subset`.

The output from `launchable subset` includes a tip to run `launchable inspect subset`:

```bash
$ launchable subset --build 123 --confidence 90% minitest test/*.rb > subset.txt

< summary table >

Run `launchable inspect subset --subset-id 26876` to view full subset details
```

Running that command will output a table containing a row for each test including:

* Rank/order
* Test identifier
* Whether the test was included in the subset
* Launchable's estimated duration for the test
  * Tests with a duration of `.001` seconds were not recognized by Launchable

{% hint style="success" %}
Note that the hierarchy level of the items in the list depends on the test runner in use.

For example, since Maven can accept a list of test _classes_ as input, `launchable inspect subset` will output a prioritized list of test _classes_. Similarly, since Cypress can accept a list of test _files_ as input, `launchable inspect subset` will output a list of prioritized test _files_. (And so on.)
{% endhint %}

## Other tips

### "Training wheels" mode with the --rest option

You can start subsetting by just splitting your existing suite into an intelligent subset and then the rest of the tests. After you've dialed in the right subset target, you can then remove the remainder and run the full suite less frequently. See the diagram below for a visual explanation.

![](../../.gitbook/assets/shift-right.png)

The middle row of the diagram shows how you can start by splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

The example below shows how you can generate a subset (`launchable-subset.txt`) and the remainder (`launchable-remainder.txt`) using the `--rest` option. Here we're using Ruby and minitest:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence 90% \
  --rest launchable-remainder.txt \
  minitest test/**/*.rb > launchable-subset.txt
```

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` that you can pass into your command to run tests in two stages. Again, using Ruby as an example:

{% hint style="info" %}
To prevent test runners from erroring out, the `--rest` file will always include at least one test, even if the subset file contains all tests (e.g. requesting a subset with `--target 100%`).
{% endhint %}

```bash
bundle exec rails test $(cat launchable-subset.txt)

bundle exec rails test $(cat launchable-remainder.txt)
```

You can remove the second part after you're happy with the subset's performance. Once you do this, make sure to continue running the full test suite at some stage as described in [Preparing your pipeline](subsetting-your-test-runs.md#preparing-your-pipeline).

### Replacing static parallel suites with a dynamic parallel subset

Some teams manually split their test suites into several "bins" to run them in parallel. This presents a challenge adopting Launchable, because you don't want to lose the benefit of parallelization.

Luckily, with **split subsets** you can replace your manually selected bins with automatically populated bins from a Launchable subset.

For example, let's say you currently run \~80 minutes of tests split coarsely into four bins and run in parallel across four workers:

* Worker 1: \~20 minutes of tests
* Worker 2: \~15 minutes of tests
* Worker 3: \~20 minutes of tests
* Worker 4: \~25 minutes of tests

With a split subset, you can generate a subset of the full 80 minutes of tests and then call Launchable once in each worker to get the bin of tests for that runner.

The high level flow is:

1. Request a subset of tests to run from Launchable by running `launchable subset` with the `--split` option. Instead of outputting a list of tests, the command will output a subset ID that you should save and pass into each runner.
2. Start up your parallel test worker, e.g. four runners from the example above
3. In each worker, request the bin of tests that worker should run. To do this, run `launchable split-subset` with:
   1. the `--subset-id` option set to the ID you saved earlier, and
   2. the `--bin` value set to `bin-number/bin-count`.
4. Run the tests in each worker.
5. After each run finishes in each worker, record test results using `launchable record tests` with the `--subset-id` option set to the ID you saved earlier.

In pseudocode:

```
# main
$ launchable record build --name $BUILD_ID --source src=.
$ launchable subset --split --confidence 90% --build $BUILD_ID bazel .
subset/12345

...

# worker 1
$ launchable split-subset --subset-id subset/12345 --bin 1/3 --rest rest.txt bazel > subset.txt
$ bazel test $(cat subset.txt)
$ launchable record tests --subset-id subset/12345 bazel .


# worker 2
$ launchable split-subset --subset-id subset/12345 --bin 2/3 --rest rest.txt bazel > subset.txt
$ bazel test $(cat subset.txt)
$ launchable record tests --subset-id subset/12345 bazel .

# worker 3
$ launchable split-subset --subset-id subset/12345 --bin 3/3 --rest rest.txt bazel > subset.txt
$ bazel test $(cat subset.txt)
$ launchable record tests --subset-id subset/12345 bazel .
```
