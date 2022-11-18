# Sending data to Launchable

First, follow the steps in the [getting-started.md](../getting-started.md "mention") guide to sign up, set your API key, install the Launchable CLI, and verify your connection.

Then return to this page to complete the two steps for sending data to Launchable:

1. Recording [build.md](../concepts/build.md "mention")s
2. Recording [test-session.md](../concepts/test-session.md "mention")s

The diagram below diagrams the high-level data flow:

![](<../.gitbook/assets/recording data@2x.png>)

## Recording builds

Each [test-session.md](../concepts/test-session.md "mention") is associated with a [build.md](../concepts/build.md "mention"). In particular, [predictive-test-selection](../features/predictive-test-selection/ "mention") selects tests based on the Git changes in a build (among other data).

To send Git changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you record test results. See [choosing-a-value-for-build-name.md](choosing-a-value-for-build-name.md "mention") for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository (or repositories) used to produce this build, such as `.` or `src`.
  * See also [recording-builds-from-multiple-repositories.md](recording-builds-from-multiple-repositories.md "mention").

## Recording test results

Launchable also uses your test results from each [test-session.md](../concepts/test-session.md "mention") to provide features.

To record tests to a test session, after running tests, point the CLI to your test report files to collect test results for the build.

Launchable uses the `<BUILD NAME>` value to connect the test results with the changes in the build:

```bash
launchable record tests --build <BUILD NAME> <TOOL NAME> <PATHS TO REPORT FILES>
```

This command varies slightly based on the test runner/build tool you use.

The CLI natively integrates with the tools below. Click on the link to view instructions specific to your tool:

* [adb.md](../resources/integrations/adb.md "mention")
* [ant.md](../resources/integrations/ant.md "mention")
* [bazel.md](../resources/integrations/bazel.md "mention")
* [behave.md](../resources/integrations/behave.md "mention")
* [ctest.md](../resources/integrations/ctest.md "mention")
* [cucumber.md](../resources/integrations/cucumber.md "mention")
* [cypress.md](../resources/integrations/cypress.md "mention")
* [googletest.md](../resources/integrations/googletest.md "mention")
* [go-test.md](../resources/integrations/go-test.md "mention")
* [gradle.md](../resources/integrations/gradle.md "mention")
* [jest.md](../resources/integrations/jest.md "mention")
* [maven.md](../resources/integrations/maven.md "mention")
* [minitest.md](../resources/integrations/minitest.md "mention")
* [nose.md](../resources/integrations/nose.md "mention")
* [nunit.md](../resources/integrations/nunit.md "mention")
* [pytest.md](../resources/integrations/pytest.md "mention")
* [robot.md](../resources/integrations/robot.md "mention")
* [rspec.md](../resources/supported-test-frameworks/rspec.md "mention")

{% hint style="info" %}
If you're not using any of these, see [raw.md](../resources/integrations/raw.md "mention") or[using-the-generic-file-based-runner-integration.md](../resources/integrations/using-the-generic-file-based-runner-integration.md "mention").
{% endhint %}

After you record test results, you can view them in the Test Sessions section of the Launchable dashboard at [app.launchableinc.com](https://app.launchableinc.com/). The CLI will also output a link to view this session's test results in the dashboard.

## Next steps

Once you've started sending your builds and test results to Launchable, you can

1. Get [test-notifications-via-slack.md](../features/test-notifications-via-slack.md "mention"), and
2. See [trends.md](../features/insights/trends.md "mention") in your test sessions,
3. Find [flaky-tests.md](../features/insights/flaky-tests.md "mention"),
4. Save time running tests and run tests earlier with [predictive-test-selection](../features/predictive-test-selection/ "mention")
