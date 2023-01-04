# Requesting and running a subset of tests

Once you've started [Broken link](broken-reference "mention"), you can connect your test runner with Launchable to request and run a subset of tests selected using Predictive Test Selection.

The diagram below illustrates the interactions between your tools, the Launchable CLI, and the Launchable platform:

![The diagram above uses the generic term test files, but the real object type may be different depending on your stack (e.g. test classes, test targets, etc.).](<../../../.gitbook/assets/subsetting diagram@2x.png>)

First, see [choosing-a-subset-optimization-target](choosing-a-subset-optimization-target/ "mention").

Then, follow instructions for to start subsetting to your pipeline:

* [subsetting-with-test-runner-integrations.md](subsetting-with-test-runner-integrations.md "mention")
  * Supports **nose** and **pytest**
* [subsetting-with-the-launchable-cli](subsetting-with-the-launchable-cli/ "mention")
  * Supports **Android Debug Bridge**, **Ant**, **Bazel**, **Behave**, **CTest**, **cucumber**, **Cypress**, **GoogleTest**, **Go** **Test**, **Gradle**, **Jest**, **Maven**, **minitest**, **pytest**, **Robot**, **Rspec**, and other/custom test runners
