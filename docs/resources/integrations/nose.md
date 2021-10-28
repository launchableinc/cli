---
description: This page outlines how the Launchable CLI interfaces with nose.
---

# nose

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

The nose plugin automatically sends test results to Launchable when you run nose with `--launchable-subset` enabled.

However, if you want to submit test reports from a full test run to help train the model, run your tests with the `--launchable-record-only` flag:

```bash
nosetests --launchable-build-number <BUILD NAME> \
  --launchable-record-only
```

### Subsetting your test runs

First, install the Launchable plugin for nose using PIP:

```bash
$ pip install nose-launchable
```

To run a meaningful subset of tests, invoke `nosetests` with three extra flags:

```bash
# subset tests with Launchable
nosetests --launchable-build-number <BUILD NAME> \
  --launchable-subset \
  --launchable-subset-options <LAUNCHABLE CLI SUBSET OPTIONS>
```

The `--launchable-build-number` flag tells Launchable which build is being tested. This should be the same value you used for `--name` in `launchable record build` before. The `--launchable-subset` flag enables subsetting.

The `--launchable-subset-options` flag tells the plugin which Launchable CLI subset options to use. For example, to use the Launchable CLI's `--target` option, the flag should look like `--launchable-subset-options '--target 10%'`. This runs a subset of the most useful test targets that will run in 10% of the full execution time. You can also use `--launchable-subset-options '--time 100'` to run a subset of the most useful test targets that will run in 100 seconds. See the [CLI reference](../cli-reference.md) for more options.

{% hint style="info" %}
The `--launchable-subset-target PERCENTAGE` option is still available; it functions the same as `--launchable-subset-options '--target PERCENTAGE'`. To accommodate future CLI options, however, we recommend using `--launchable-subset-options` where convenient.
{% endhint %}

### Running a subset across parallel nose invocations

Some teams manually split their test suites into several "bins" to run them in parallel. This presents a challenge adopting Launchable, because you don't want to lose the benefit of parallelization. Luckily, with **split subsets** you can replace your manually selected bins with automatically populated bins from a Launchable subset.

For example, let's say you currently run \~35 minutes of tests split coarsely into four bins and run in parallel across four workers:

* Worker 1: \~20 minutes of tests
* Worker 2: \~15 minutes of tests

With a split subset, you can call Launchable once in each worker to get the bin of tests from a subset for that runner.

The high level flow is:

1. Manually record a build (see [Recording builds](../../sending-data-to-launchable/#Recording-builds))
2. Manually record a test session against that build and store the value returned from Launchable for use later
3. In each nosetests invocation, request the bin of tests that worker should run. To do this, run `nosetests` with:
   1. the `--launchable-test-session` option set to the session ID value you saved earlier, and
   2. the `--bin` value in `--launchable-subset-options`set to `bin-number/bin-count`.

In pseudocode:

```
# main
$ launchable record build --name 12345 --source src=.
$ launchable record session --build 12345
builds/12345/test_sessions/678910

# machine 1
$ nosetests --launchable-subset --launchable-test-session builds/12345/test_sessions/678910 --launchable-subset-options "--target 40% --bin 1/2"

# machine 2
$ nosetests --launchable-subset --launchable-test-session builds/12345/test_sessions/678910 --launchable-subset-options "--target 40% --bin 2/2"
```

### Troubleshooting

If you encounter issues running nose with the Launchable plugin, you can set the `LAUNCHABLE_DEBUG` environment variable to `1` before running tests to print debug logs.

```bash
# enable debug logs
export LAUNCHABLE_DEBUG=1

# run tests with Launchable
nosetests --launchable-subset ...
```

### Development

The Launchable nose plugin is open source and [available on GitHub](https://github.com/launchableinc/nose-launchable). Pull requests are always appreciated!
