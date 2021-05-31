# Bazel

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

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> bazel .
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../resources/always-run.md).
{% endhint %}

## Subsetting tests

Subsetting instructions differ depending on whether you plan to [shift tests left](../#shift-left) or [shift tests right](../#shift-right):

### Shift left

First, set up a new test execution job/step/pipeline to run earlier in your software development lifecyle.

Then, to retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    bazel > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
bazel test $(cat launchable-subset.txt)
```

Make sure to continue running the full test suite at some stage. Run `launchable record build` and `launchable record tests` for those runs to continually train the model.

### Shift right

The [shift right](../#shift-right) diagram suggests first splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

To retrieve a subset of tests, first pass the full list of test candidates to `launchable subset`. For example:

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    --rest launchable-remainder.txt \
    bazel > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.
* The `--rest` option writes all the other tests to a file so you can run them separately.

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` that you can pass into your command to run tests in two stages:

```bash
bazel test $(cat launchable-subset.txt)

bazel test $(cat launchable-remainder.txt)
```

You can remove the second part after we've let you know that the model is sufficiently trained. Once you do this, make sure to continue running the full test suite at some stage. Run `launchable record build` and `launchable record tests` for those runs to continually train the model.

## --build-event-json-file option

In some environments, the report files of previous build are remaining. In that case, `launchable record tests` command always has to send results of previous builds.
You should use `--build_event_json_file` option of [the bazel command](https://docs.bazel.build/versions/4.0.0/build-event-protocol.html) and `--build-event-json` option of the bazel plugin of the CLI to avoid it. the CLI chooses the report files from the build event json files.

1. Add `--build_event_json_file` option to bazel test commands.

```bash
bazel test $(cat launchable-subset.txt) --build_event_json_file=build_event_subset.json

bazel test $(cat launchable-remainder.txt) --build_event_json_file=build_event_remainder.json
```

2. Set the build event json files to `--build-event-json` option of the `record tests` command

```bash
launchable record tests --build <BUILD NAME> bazel --build-event-json build_event_subset.json --build-event-json build_event_remainder.json .
```
