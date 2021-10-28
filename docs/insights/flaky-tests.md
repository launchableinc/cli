# Flaky Test Insights

## About flaky tests

Flaky tests are automated tests that fail randomly during a run for reasons not related to the code changes being tested. They are often caused by timing issues, concurrency problems, or the presence of other workloads in the system.

Flaky tests are a common problem for many development teams especially as test suites grow. They are more common at higher levels of the Test Pyramid, especially in UI tests and system tests.

Like the fictional boy who cried “wolf”, tests that send a false signal too often are sometimes ignored. Or worse, people spend really time and effort trying to diagnose a failure, only to discover that it has nothing to do with their code changes. When flakiness occurs with a lot of tests it can make people weary of all tests and all failures—not just flaky tests—causing a loss of trust in tests.

Tests that produce flaky results should be repaired or removed from the test suite.

## Flaky Test Insights

To help with this, Launchable can now analyze your test runs to identify flaky tests in your suite.

All you have to do is start [sending data to Launchable](../sending-data-to-launchable/). After that, the **Flaky tests** page should be populated within a few days.

Launchable assigns each test a flakiness score from 0-1. Tests with higher scores have been identified as more flaky by Launchable:

![Flaky Tests Insights](../.gitbook/assets/flaky-tests-screen.png)

You can use this list to investigate and fix your flaky tests. Flaky tests are re-analyzed approximately once per day.
