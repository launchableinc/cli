# Test session

## Overview

After you run your test suite in your CI system against a [build.md](build.md "mention"), you record your test results in Launchable using the CLI. Those results are recorded against a **test session**.

Therefore, a test session is a record of:

1. A certain list of tests that ran
2. How long each test took to run
3. Each test's pass/fail/skipped status
4. Aggregate statistics about the above (e.g. total duration, total count, and total passed/failed/skipped counts)

![Relationship between workspaces, builds, test sessions, and tests](<../.gitbook/assets/Object model June 2022@2x.png>)

## Test sessions across Launchable

Test sessions are a key Launchable concept and as such are used for lots of purposes.

### Test results and reports

[#test-results-and-reports](../#test-results-and-reports "mention") are organized by test session. The test session details page shows test counts, total duration, and failed tests per test session.

### Insights

Some [#insights](../#insights "mention"), particularly [#trends](../#trends "mention"), are aggregated by test session. For example, the _Test session duration_ and _Test session frequency_ insights show data aggregated across test sessions in a workspace.

### Predictive Test Selection

Test sessions are used for evaluating [predictive-test-selection](../features/predictive-test-selection/ "mention") models. For example, the Confidence curve is built by running existing test sessions through the model to see how long it would have taken for a model to find a failing test in a failing run. Therefore, the length of the X-axis of the Confidence curve corresponds with the length of your longest recent test session.

## Test session layouts

Different teams organize their tests in different ways, which we call "layouts."

Your team's layout impacts how you should record tests in a workspace. This section outlines a few common layouts, including guidance on when you might want to split your runs into multiple test sessions against a single buikld.

{% hint style="info" %}
See [#test-suites-and-workspaces](workspace.md#test-suites-and-workspaces "mention") for guidance on splitting tests between _workspaces_.
{% endhint %}

### Default layout

In many cases, builds and test sessions map 1:1. For example, a developer pushes a change, the change is built, and the build is tested. The test runner (e.g. pytest) is run once with a single list of tests.

The CLI handles this default case without any extra steps. Just run `launchable record tests` at the end of your run to capture test results to a single session.

![](<../.gitbook/assets/Test session definition@2x.png>)

### Running tests in different environments

Some teams run their tests across several environments. For example, UI tests might be run in different browsers. In this case, your build will have multiple test sessions per build: one per environment.

![One test session per environment (purple box)](<../.gitbook/assets/Test session definition@2x (3).png>)

Test sessions have an optional attribute called `flavor` that handles this. To implement this test session layout, see [use-flavors-to-run-the-best-tests-for-an-environment.md](../sending-data-to-launchable/use-flavors-to-run-the-best-tests-for-an-environment.md "mention").

### Running tests in parallel

Parallelization is a highly effective strategy for reducing test feedback delay. Depending on how you parallelize your tests and how you want to analyze them in Launchable, you may want to create multiple test sessions per build.

#### Automatically generated parallel bins

Some test runners support automatic test parallelization. In this scenario, the test runner typically lets you define how many workers to distribute tests across via a configuration option. You kick off tests once and then the test runner distributes tests into bins for each worker automatically. At the end of the run, test reports are often recorded to a single location on the same machine where tests were kicked off.

This scenario _does not_ warrant separate test sessions for each worker. Since the parallelization process is automatic and opaque, instrumentation is the same as the **default layout** described above.

![Yellow boxes are invisible](<../.gitbook/assets/Test session definition@2x (1).png>)

The main difference to note is that the test session duration shown in Launchable will be higher than the "wall clock time" perceived by developers since test reports include machine time and don't know about parallelization. To get the wall clock time, divide the test session duration by your parallelization factor.

{% hint style="warning" %}
If your test runner are automatically distributes tests to parallel workers but _does not_ deposit test result files to a location on the original machine, you'll need to manually create a test session before you run tests. See [#combining-test-reports-from-multiple-runs](../sending-data-to-launchable/managing-complex-test-session-layouts.md#combining-test-reports-from-multiple-runs "mention").
{% endhint %}

#### Static bins

Some teams parallelize their tests by manually splitting them into _static_ lists of tests (otherwise known as **bins**). They might organize tests by functional area (for easier triage) or by typical duration (to create bins of roughly equal length), or something else.

In this scenario, the test runner is individually invoked once per bin, like this:

![](<../.gitbook/assets/Test session definition@2x (2).png>)

This gives you two options for aggregating reports into test sessions:

1. **One session per bin** _(purple boxes)_. This option is preferred if:
   1. You have fewer than \~10 bins, and/or
   2. You plan to use Predictive Test Selection, because a 1:1:1 relationship between test runner invocations, test sessions, and subset requests is preferred for best performance
2. **One session per pipeline** _(orange box)_. This option is preferred if:
   1. You have more than \~10 bins, because at this scale it becomes less useful to analyze tests at the bin level and more useful to analyze them at the pipeline level

Ultimately, though, you are the expert on your test suite layout, so you have the option to aggregate at the hierarchy level that makes sense to you. Depending on your choice, you may need to see [#managing-test-sessions-explicitly](test-session.md#managing-test-sessions-explicitly "mention").

### Managing test sessions explicitly

In most cases, the CLI will manage test sessions on your behalf. The `launchable record tests` command and `launchable subset` command will automatically create a test session where needed.

However, if your build, test, and/or test report collection processes occur across several machines/processes, you'll probably need to manage test sessions explicitly. This requires explicitly creating a test session using `launchable record session` and then passing the session value through your pipeline for use in `launchable subset` and `launchable record tests`.

The page [managing-complex-test-session-layouts.md](../sending-data-to-launchable/managing-complex-test-session-layouts.md "mention") describes how to do this.

##
