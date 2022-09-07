# Observing subset behavior

Sometimes teams want to observe the potential impact and behavior of running subsets in a real environment before they start using them. In other words, they want to measure subsets' real world efficacy against the simulation shown in [choosing-a-subset-optimization-target.md](../choosing-a-subset-optimization-target.md "mention").

You can do this using **observation mode**, which is a special usage mode of `launchable subset`.

To enable observation mode, just add `--observation` to the `launchable subset` command you added to your pipeline after following [requesting-and-running-a-subset-of-tests](../requesting-and-running-a-subset-of-tests/ "mention"):

```bash
launchable subset \
  --observation
  --target 30%
  ... [other options]
```

{% hint style="info" %}
If your pipeline requires you to create a test session separately using `launchable record session` (after following the instructions in [managing-complex-test-session-layouts.md](../../../sending-data-to-launchable/managing-complex-test-session-layouts.md "mention")), add the `--observation` option to _that_ command instead of `launchable subset`.

```bash
launchable record session \
  --build $BUILD_NAME \
  --observation
  ... [other options]
```

Observation mode is a property of a [test-session.md](../../../concepts/test-session.md "mention"), not a [subset.md](../../../concepts/subset.md "mention").
{% endhint %}

When observation mode is enabled for a test session, the output of each `launchable subset` command made against that test session will always include all tests, but the recorded results will be presented separately so you can compare running the subset against running the full suite.

For example, let's imagine you have a test suite with 100 tests that each take 1 second to run (100 seconds in total):

* By default, if you requested a subset of this test suite with a 30% duration optimization target, the subset output would include 30 tests.
* However, with observation mode enabled, if you requested a subset of this test suite with a 30% duration optimization target, the subset output would include all 100 tests. When you record results, Launchable will recognize this "full session" as a subset observation session.

Because you marked the session as an observation session, Launchable can analyze what would have happened if you had actually run a subset of tests, such as whether the subset would have caught a failing session, and how much time you could have saved by running only the subset of tests:

<figure><img src="../../../.gitbook/assets/2022-09-07 Observation mode.png" alt=""><figcaption></figcaption></figure>

You can use this data to compare your real-world results with your **Confidence curve** (see [choosing-a-subset-optimization-target.md](../choosing-a-subset-optimization-target.md "mention")).
