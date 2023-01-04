# Unhealthy Tests

Tests are hard to maintain. Once you write them, they have tendency to stick around, even when it’s no longer clear what value they provide, or when they are hurting more than helping.

SMEs working on maintaining those tests often struggle to make convincing arguments as to what work needs to be done to improve the effectiveness of tests, and get frustrated.

The overall quality of tests suffers, and in the worst case, the annoyance of the tests go too high and developers lose trust in the tests.

Hence the new **Unhealthy Tests** page in Launchable! This page surfaces tests that exhibit specific issues so that you can investigate and make changes if necessary.

{% hint style="info" %}
Unhealthy Test stats are aggregated at the 'altitude' that your test runner uses to run tests. See [#subset-altitude-and-test-items](../../concepts/subset.md#subset-altitude-and-test-items "mention") for more info on this concept.
{% endhint %}

<figure><img src="../../.gitbook/assets/Screenshot 2022-12-13 at 12.53.54 PM.png" alt=""><figcaption></figcaption></figure>

## Never Failing Tests

Tests that never fail are like cats who never catch any mice. They take up execution time and require maintenance, but yet they may not add value. For each test, ask yourself if the test provides enough value to justify its execution time. Consider moving the test to the right so that it runs less frequently.

{% hint style="info" %}
A test must run at least **five** (5) times in order to be considered.
{% endhint %}

## Flaky Tests

Flaky tests are automated tests that fail randomly during a run for reasons not related to the code changes being tested. They are often caused by timing issues, concurrency problems, or the presence of other workloads in the system.

{% hint style="info" %}
Soon, [flaky-tests.md](flaky-tests.md "mention") will migrate to this page. In the meantime, use the **Flaky Tests** page instead.
{% endhint %}

## Tests that take too long <a href="#tests-that-take-too-long" id="tests-that-take-too-long"></a>

Slow tests are like gunk that builds up in your engine. Over time they slow down your CI cycle.

{% hint style="info" %}
Coming soon.
{% endhint %}

## Tests that fail too often <a href="#tests-that-fail-too-often" id="tests-that-fail-too-often"></a>

Tests that fail _too_ often are suspicious. Perhaps they are flaky. Perhaps they are fragile / high maintenance. Perhaps they are testing too many things in one shot.

{% hint style="info" %}
Coming soon.
{% endhint %}
