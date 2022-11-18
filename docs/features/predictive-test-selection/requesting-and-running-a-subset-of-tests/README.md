# Requesting and running a subset of tests

Once you've started [training-a-predictive-model-with-your-data.md](../training-a-predictive-model-with-your-data.md "mention"), you can connect your test runner with Launchable.

We strongly suggest that you request and run a 100% subset of tests (i.e. run all the tests you normally would) before you actually run partial subsets in your pipeline. That way you can identify and fix any integration issues.

The high level flow for subsetting is:

1. Get the full list of tests (or test files, targets, etc.) and pass that to `launchable subset` along with:
   1. an optimization target for the subset
   2. a build name, so Launchable can choose the best tests for the changes in the build being tested
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

The diagram below illustrates the interactions between your tools, the Launchable CLI, and the Launchable platform:

![](<../../../.gitbook/assets/subsetting diagram@2x.png>)

{% hint style="info" %}
The diagram above uses the generic term test _files_, but the real object type may be different depending on your stack (e.g. test _classes_, test _targets_, etc.).
{% endhint %}

## Requesting and running a subset

Use `launchable subset` to request a subset of tests. You'll run this command before your normal test runner command.

Here's an example using Ruby/minitest. For integration, we're using an optimization target of 100% so that all tests are still run:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target 100% \
  minitest test/**/*.rb > launchable-subset.txt
```

The `--build` option should use the same `<BUILD NAME>` value that you used in `launchable record build`.

This creates a file called `launchable-subset.txt` that you can pass into your test runner.

Again, with Ruby/minitest:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

Subsetting instructions depend on the test runner or build tool you use to run tests. Click the appropriate link below to get started:

* [Android Debug Bridge (adb)](../../../resources/integrations/adb.md#subsetting-your-test-runs)
* [Ant](../../../resources/integrations/ant.md#subsetting-your-test-runs)
* [Bazel](../../../resources/integrations/bazel.md#subsetting-your-test-runs)
* [Behave](../../../resources/integrations/behave.md#subsetting-your-test-runs)
* [CTest](../../../resources/integrations/ctest.md#subsetting-your-test-runs)
* [Cypress](../../../resources/integrations/cypress.md#subsetting-your-test-runs)
* [GoogleTest](../../../resources/integrations/googletest.md#subsetting-your-test-runs)
* [Go Test](../../../resources/integrations/go-test.md#subsetting-your-test-runs)
* [Gradle](../../../resources/integrations/gradle.md#subsetting-your-test-runs)
* [Jest](../../../actions/resources/supported-languages/jest.md#subsetting-your-test-runs)
* [Maven](../../../resources/integrations/maven.md#subsetting-your-test-runs)
* [minitest](../../../resources/integrations/minitest.md#subsetting-your-test-runs)
* [nose](../../../resources/integrations/nose.md#subsetting-your-test-runs)
* [pytest](../../../resources/integrations/pytest.md#subsetting-your-test-runs-pytest-plugin)
* [Robot](../../../resources/integrations/robot.md#subsetting-your-test-runs)
* [RSpec](../../../resources/integrations/rspec.md#subsetting-your-test-runs)

{% hint style="info" %}
If you're not using any of these, use the [generic 'file-based' runner integration](../../../resources/integrations/using-the-generic-file-based-runner-integration.md), the [`raw` profile for custom test runners](../../../resources/integrations/raw.md), or [request a plugin](mailto:support@launchableinc.com?subject=Request%20a%20plugin).
{% endhint %}

## Checking for integration issues

{% hint style="info" %}
Coming soon!
{% endhint %}
