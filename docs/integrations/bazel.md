# Bazel

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

Subsetting instructions differ slightly depending on whether you plan to [shift tests left](../#shift-left) or [shift tests right](../#shift-right):

### Shift left

To retrieve a subset of tests, first ask Bazel for all the test targets you would normally run. For example:

```bash
# list up all test targets in the whole workspace
bazel query 'tests(//...)'
```

Then **pipe** those results into `launchable subset bazel` to get a subset of test targets to run from Launchable:

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    bazel > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with. As the model learns from your builds, the tests in the subset will become more and more relevant.

This creates a file called `launchable-subset.txt` you can pass to Bazel to run:

```bash
# run only the subset of test targets
bazel test $(cat launchable-subset.txt)
```

Make sure to continue running the full test suite at some point in your software delivery lifecycle. When you do, keep running `launchable record build` and `launchable record tests` for those runs to continually train the model.

### Shift right

The [shift right](../#shift-right) diagram suggests first splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

Once you're comfortable with the subset of dynamically selected tests, you can remove the "rest of the tests" part to increase throughput.

To do this, first ask Bazel for all the test targets you would normally run. For example:

```bash
# list up all test targets in the whole workspace
bazel query 'tests(//...)'
```

Then **pipe** those results into `launchable subset bazel` to get a subset of test targets to run from Launchable:

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    --rest launchable-remainder.txt
    bazel > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with. As the model learns from your builds, the tests in the subset will become more and more relevant.

The `--rest` option writes all the other test targets to a file so you can run them separately.

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` you can pass to Bazel to run:

```bash
# run only the subset of test targets
bazel test $(cat launchable-subset.txt)

# run the rest of the targets
bazel test $(cat launchable-remainder.txt)
```

After a few runs, you can remove the second part. Once you do this, make sure to continue running the full test suite at some point in your software delivery lifecycle. When you do, keep running `launchable record build` and `launchable record tests` for those runs to continually train the model.

## Recording test results

After running tests, simply point to the Bazel workspace \(`.`\) to collect test results:

```bash
launchable record tests --build <BUILD NAME> bazel .
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../resources/always-run.md).
{% endhint %}

