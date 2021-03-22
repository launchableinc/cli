# Robot

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

To select a meaningful subset of tests, use `--dryrun` option to create a file listing all test cases (e.g. `dryrun.xml`). Then pass that file to `launchable subset` like this:

```bash
robot --dryrun -o dryrun.xml
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  robot dryrun.xml > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with.

This command creates a `launchable-subset.txt` file that contains the subset of tests that should be run. You can now invoke minitest to run exactly those tests:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

## Recording test results

Robot outputs a xUnit compatible report by default: see [Robot - Output file](https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#output-file).

After running tests, point to files that contains all the generated test report XML files:

```bash
# run the tests however you normally do
robot .

launchable record tests --build <BUILD NAME> robot output.xml
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}
