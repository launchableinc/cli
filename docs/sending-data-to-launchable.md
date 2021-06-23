# Sending data to Launchable

## Getting started

First, follow the steps in the [Getting started](https://github.com/launchableinc/cli/tree/0b50d53f548510b676558981ee9065a7833c3657/getting-started.md) guide to install the Launchable CLI, set your API key, and verify your connection.

Then return to this page to complete the two steps for sending data:

1. Recording builds
2. Recording test results

## Recording builds

Launchable learns from and selects tests based on the Git changes in a **build**. To send changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](resources/build-names.md) for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`. See [Data privacy and protection](security/data-privacy-and-protection.md) for more info.

## Recording test results

Launchable also learns from your test results. After running tests, point the CLI to your test report files to collect test results for the build. Launchables uses the `<BUILD NAME>` value to connect the test results with the changes in the build:

```bash
launchable record tests --build <BUILD NAME> <TOOL NAME> <PATHS TO REPORT FILES>
```

The CLI natively integrates with the tools below. Click on the link to view instructions specific to your tool:

* [Android Debug Bridge \(ADB\)](test-runners/adb.md)
* [Ant](test-runners/ant.md#recording-test-results)
* [Bazel](test-runners/bazel.md#recording-test-results)
* [Behave](test-runners/behave.md#recording-test-results)
* [CTest](test-runners/ctest.md#recording-test-results)
* [Cypress](test-runners/cypress.md#recording-test-results)
* [GoogleTest](test-runners/googletest.md#recording-test-results)
* [Go Test](test-runners/go-test.md#recording-test-results)
* [Gradle](test-runners/gradle.md#recording-test-results)
* [Maven](test-runners/maven.md#recording-test-results)
* [Minitest](test-runners/minitest.md#recording-test-results)
* [Nose](test-runners/nose.md#recording-test-results)
* [Robot](test-runners/robot.md#recording-test-results)
* [RSpec](test-runners/rspec.md#recording-test-results)

\(Not using any of these? Try the [generic file based test runner](resources/file.md) option.\)

