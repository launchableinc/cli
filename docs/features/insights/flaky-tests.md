# Flaky Tests

## About flaky tests

Flaky tests are automated tests that fail randomly during a run for reasons not related to the code changes being tested. They are often caused by timing issues, concurrency problems, or the presence of other workloads in the system.

Flaky tests are a common problem for many development teams especially as test suites grow. They are more common at higher levels of the Test Pyramid, especially in UI tests and system tests.

Like the fictional boy who cried “wolf”, tests that send a false signal too often are sometimes ignored. Or worse, people spend really time and effort trying to diagnose a failure, only to discover that it has nothing to do with their code changes. When flakiness occurs with a lot of tests it can make people weary of all tests and all failures—not just flaky tests—causing a loss of trust in tests.

Tests that produce flaky results should be repaired or removed from the test suite.

## Flaky Test Insights

To help with this, Launchable can analyze your test runs to identify flaky tests in your suite.

All you have to do is start [sending data to Launchable](../../sending-data-to-launchable/). After that, the **Flaky tests** page should be populated within a few days.

**However, for flakiness scores to populate, you need to run the same test multiple times against the same** [build.md](../../concepts/build.md "mention"). In other words, you need to have a retry mechanism in place to re-run tests when they fail. (This is usually already the case for test suites with flaky tests.)

Launchable re-analyzes your test sessions to extract flakiness data every day.

![](<../../.gitbook/assets/2022-08-11 Flaky tests - with new scores.png>)

### Flakiness score

A test is considered flaky if you run it multiple times against the same build and sometimes it passes and sometimes it fails.

The **flakiness score** for a test represents the probability that a test _fails_ but eventually _passes_ if you run it repeatedly.

For example, let's say you have a test called `myTest1` which has a flakiness score of 0.1. This means that if this test failed against 10 different commits, in 1 of those 10 commits, that failure was not a true failure. If you run that test repeatedly, it eventually _passes_. This test is slightly flaky.

Similarly, another test called `myTest2` has a flakiness score of 0.9. If this test failed against 10 different commits, in 9 out of those 10 commits, you saw a false failure that retry will yield a _passing_ result. That test is very flaky and should be fixed.

### Total duration

The dashboard also includes the **total duration** of a flaky test. Since flaky tests are often retried multiple times, this adds up to lots of extra time running tests.

The total duration is useful for prioritizing which flaky tests to fix _first_.

For example, you might have a test that's very flaky (i.e. it has a high flakiness score) but either doesn't take very long to run each time, or it doesn't run very often, or both. In comparison, you might have a test that is less flaky but takes a very long time to run -- so you'll probably want to fix that first.

{% hint style="info" %}
The table is _currently_ sorted by flakiness score in descending order, not total duration.
{% endhint %}
