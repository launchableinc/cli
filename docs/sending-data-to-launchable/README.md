# Sending data to Launchable

## Overview

First, follow the steps in the [Getting started](../getting-started/) guide to install the Launchable CLI, set your API key, and verify your connection.

Then return to this page to complete the two steps for sending data:

1. Recording builds
2. Recording test results

The diagram below diagrams the high-level data flow:

![](../.gitbook/assets/sending-data-diagram.png)

## Recording builds

Launchable learns from and selects tests based on the Git changes in a **build**. To send changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request record test results. See [Choosing a value for `<BUILD NAME>`](choosing-a-value-for-build-name.md) for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository \(or repositories\) used to produce this build, such as `.` or `src`. See [Data privacy and protection](../policies/data-privacy-and-protection/) for more info.

## Recording test results

Launchable also learns from your test results. After running tests, point the CLI to your test report files to collect test results for the build. Launchable uses the `<BUILD NAME>` value to connect the test results with the changes in the build:

```bash
launchable record tests --build <BUILD NAME> <TOOL NAME> <PATHS TO REPORT FILES>
```

The CLI natively integrates with the tools below. Click on the link to view instructions specific to your tool:

* [Android Debug Bridge \(adb\)](../resources/integrations/adb.md)
* [Ant](../resources/integrations/ant.md#recording-test-results)
* [Bazel](../resources/integrations/bazel.md#recording-test-results)
* [Behave](../resources/integrations/behave.md#recording-test-results)
* [CTest](../resources/integrations/ctest.md#recording-test-results)
* [Cypress](../resources/integrations/cypress.md#recording-test-results)
* [GoogleTest](../resources/integrations/googletest.md#recording-test-results)
* [Go Test](../resources/integrations/go-test.md#recording-test-results)
* [Gradle](../resources/integrations/gradle.md#recording-test-results)
* [Maven](../resources/integrations/maven.md#recording-test-results)
* [Minitest](../resources/integrations/minitest.md#recording-test-results)
* [Nose](../resources/integrations/nose.md#recording-test-results)
* [NUnit](../resources/integrations/nunit.md#recording-test-results)
* [Pytest](../resources/integrations/pytest.md#recording-test-results)
* [Robot](../resources/integrations/robot.md#recording-test-results)
* [RSpec](../resources/integrations/rspec.md#recording-test-results)

\(Not using any of these? Try the [generic file based test runner](using-the-generic-file-based-runner-integration.md) option.\)

## Next steps

Once you've started sending your builds and test results to Launchable, you can analyze your [flaky tests](../insights/flaky-tests.md) and start [subsetting your test runs](../actions/subsetting-your-test-runs.md).

