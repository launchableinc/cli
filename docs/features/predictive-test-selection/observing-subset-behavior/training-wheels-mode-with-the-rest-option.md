# "Training wheels" mode with the --rest option

{% hint style="warning" %}
This approach has been deprecated.

It's still supported, but we strongly suggest using the method described in [.](./ "mention") instead.
{% endhint %}

You can start subsetting by just splitting your existing suite into an intelligent subset and then the rest of the tests. After you've dialed in the right subset target, you can then remove the remainder and run the full suite less frequently. See the diagram below for a visual explanation.

![](<../../../.gitbook/assets/training wheels.png>)

The middle row of the diagram shows how you can start by splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

The example below shows how you can generate a subset (`launchable-subset.txt`) and the remainder (`launchable-remainder.txt`) using the `--rest` option. Here we're using Ruby and minitest:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence 90% \
  --rest launchable-remainder.txt \
  minitest test/**/*.rb > launchable-subset.txt
```

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` that you can pass into your command to run tests in two stages. Again, using Ruby as an example:

{% hint style="info" %}
To prevent test runners from erroring out, the `--rest` file will always include at least one test, even if the subset file contains all tests (e.g. requesting a subset with `--target 100%`).
{% endhint %}

```bash
bundle exec rails test $(cat launchable-subset.txt)

bundle exec rails test $(cat launchable-remainder.txt)
```

You can remove the second part after you're happy with the subset's performance. Once you do this, make sure to continue running the full test suite at some stage as described in [Preparing your pipeline](training-wheels-mode-with-the-rest-option.md#preparing-your-pipeline).
