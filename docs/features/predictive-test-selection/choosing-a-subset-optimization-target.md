# Choosing a subset optimization target

The optimization target you choose determines how Launchable populates a subset with tests. You can use the **Confidence** **curve** shown on the Simulate page in the Launchable dashboard to choose an optimization target.

![](<../../.gitbook/assets/2022-08-18 confidence curve.png>)

### Confidence target (`--confidence`)

{% hint style="info" %}
The confidence target is designed for use with test suites where the list of tests in each [test-session.md](../../concepts/test-session.md "mention") used to train your model is the same each time.

If your sessions have variable test lists, use the percentage time target instead.
{% endhint %}

**Confidence** is shown on the y-axis of a confidence curve.

Confidence is the probability that the subset will catch a failing session.

When you request a subset using `--confidence 90%`, Launchable will populate the subset with relevant tests up to the corresponding expected duration value on the x-axis. For example, if the corresponding duration value for 90% confidence is 3 minutes, Launchable will populate the subset with up to 3 minutes of the most relevant tests for the changes in that build. This is useful to start with because the duration should decrease over time as Launchable learns more about your changes and tests.

{% hint style="warning" %}
It's possible for all tests to be returned in a subset request when you use `--confidence`.

For example, let's say you request a subset with a 90% confidence target, which corresponds to 30 minutes of tests on the X-axis of your workspace's confidence curve. If the total estimated duration of the request's [#input-test-list](../../concepts/subset.md#input-test-list "mention") is less than 30 minutes, then all of the input tests will be returned in the subset.

This is why the confidence target should only be used with test suites that have consistent test lists.
{% endhint %}

### Fixed time target (`--time`)

{% hint style="info" %}
The fixed time target is designed for use with test suites where the total duration of each run used to train the model is relatively stable. If your runs have highly variable duration, the percentage time target may be more useful.
{% endhint %}

**Time** is shown on the x-axis of a confidence curve. When you request a subset using `--time 10m`, Launchable will populate the subset with up to 10 minutes of the most relevant tests for the changes in that build. This is useful if you have a maximum test runtime in mind.

{% hint style="warning" %}
It's possible for all tests to be returned in a subset request when you use `--time`.

For example, let's say you request a subset with a time target of 30 minutes. If the total estimated duration of the request's [#input-test-list](../../concepts/subset.md#input-test-list "mention") is less than 30 minutes, then all of the input tests will be returned in the subset.

This is why the time target should only be used with test suites that have consistent test lists.
{% endhint %}

### Percentage time target (`--target`)

{% hint style="info" %}
**Percentage time** is not yet shown in the Launchable dashboard.
{% endhint %}

When you request a subset using `--target 20%`, Launchable will populate the subset with 20% of the expected duration of the most relevant tests. For example, if the expected duration of the full list of tests passed to `launchable subset` is 100 minutes, Launchable will return up to 20 minutes of the most relevant tests for the changes in that build.

This is useful if your test sessions vary in duration.
