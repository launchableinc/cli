# Sending data to Launchable

To start using Launchable's features, you need to start sending build and test data from your CI pipeline to your Launchable workspace.

## Integration options

We offer a variety of integration options, depending on your toolchain:

* [CI integrations](using-ci-integrations/)
  * Supports **GitHub Actions**
* [Test runner integrations/plugins](using-test-runner-integrations.md)
  * Supports **pytest** and **nose**
* [Launchable CLI](using-the-launchable-cli/)
  * Supports **Android Debug Bridge**, **Ant**, **Bazel**, **Behave**, **CTest**, **cucumber**, **Cypress**, **GoogleTest**, **Go** **Test**, **Gradle**, **Jest**, **Maven**, **minitest**, **pytest**, **Robot**, **Rspec**, and other/custom test runners

## Next steps

Once you've started sending your builds and test results to Launchable, you can

1. Get [test-notifications-via-slack.md](../features/test-notifications-via-slack.md "mention"), and
2. See [trends.md](../features/insights/trends.md "mention") in your test sessions,
3. Find [unhealthy-tests.md](../features/insights/unhealthy-tests.md "mention"),
4. Save time running tests and run tests earlier with [predictive-test-selection](../features/predictive-test-selection/ "mention")
