# Cypress

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

To select a meaningful subset of tests, first pipe a list of all test files to the Launchable CLI \(`cypress/integration` is the [default directory](https://docs.cypress.io/guides/core-concepts/writing-and-organizing-tests.html#Test-files) for test files, so you'll need to change this if your tests live in a different directory\):

```bash
find ./cypress/integration | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  cypress > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with.

This command creates a `launchable-subset.txt` file that contains the subset of tests that should be run. You can now invoke Cypress to run exactly those tests:

```bash
cypress run --spec "$(cat launchable-subset.txt)"
```

## Recording test results

Cypress provides a JUnit report runner: see [Reporters \| Cypress Documentation](https://docs.cypress.io/guides/tooling/reporters.html).

After running tests, point to files that contains all the generated test report XML files:

```bash
# run the tests however you normally do, then produce a JUnit XML file
cypress run --reporter junit --reporter-options "mochaFile=report/test-output-[hash].xml"

launchable record tests --build <BUILD NAME> cypress ./report/*.xml
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](https://github.com/launchableinc/cli/tree/a54931964341f26ce0a5e73869587a66af00e05c/docs/integrations/recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests cypress --help`

