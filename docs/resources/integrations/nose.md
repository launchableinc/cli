---
description: This page outlines how the Launchable CLI interfaces with Nose.
---

# Nose

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

The Nose plugin automatically sends test results to Launchable when you run Nose with `--launchable-subset` enabled.

However, if you want to submit test reports from a full test run to help train the model, run your tests with the `--launchable-record-only` flag:

```bash
nosetests --launchable-build-number <BUILD NAME> \
  --launchable-record-only
```

### Subset your test runs

First, install the Launchable plugin for Nose using PIP:

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

### Troubleshooting

If you encounter issues running Nose with the Launchable plugin, you can set the `LAUNCHABLE_DEBUG` environment variable to `1` before running tests to print debug logs.

```bash
# enable debug logs
export LAUNCHABLE_DEBUG=1

# run tests with Launchable
nosetests --launchable-subset ...
```

### Development

The Launchable Nose plugin is open source and [available on GitHub](https://github.com/launchableinc/nose-launchable). Pull requests are always appreciated!

