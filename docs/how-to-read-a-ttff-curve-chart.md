# How to read a TTFF Curve chart

A key artifact generated for impact analysis is a **Time to First Failure \(TTFF\) Curve** chart. This curve demonstrates the real-world performance of the specific reordering model we created with your data.

To create this curve, we run many historical test sessions through the model. These are test sessions that really happened but weren't used them to train the model. The model hasn’t "seen" them before.

We let the model reorder tests from the session into an optimized sequence. We then find the first test in the optimized sequence that _actually_ failed during the original execution. We do this with enough test sessions so that we can stack them up in ascending order of TTFF, revealing the curve.

Here’s an example:

![A demonstration Confidence Curve chart](static/img/rocketcar-TTFF-curve.svg)

The x-axis represents **Test session duration percentage**, and the y-axis represents **First failure percentile**.

**Test session duration percentage** shows the percentage of the test session duration that's run so far. It’s normalized to a percentage in order to accommodate different different test session durations. Note that value is based on execution duration, not the _number_ of tests that ran.

{% hint style="info" %}
**A note on parallelization:**

The Test session duration percentage calculation assumes that tests are run sequentially in a single run, which doesn't happen when tests are run in parallel. In that case, the test session duration used is the sum of all the test durations across all the parallel runs in a given session.
{% endhint %}

**First Failure percentile** shows the percentage of test sessions where the first test failure was found _on or before_ the corresponding test time percentage.

From the above example: With Launchable reordering tests, in 90% of test sessions \(Y-axis\), the first test failure was found within 20% of the test session duration \(X-axis\) versus 73% of the test session duration \(X-axis\) without Launchable. This shows how you have to run more tests to find the first failure if your test sequence is not optimized.

Similarly, if you only run a fixed 20% test session duration \(X-axis\), Launchable should find the first failure in 90% of those runs \(Y-axis\). Without Launchable, only 50% of runs \(Y-axis\) will reveal a failure.

