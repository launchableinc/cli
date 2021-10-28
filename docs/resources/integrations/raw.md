---
description: >-
  This page outlines how the Launchable CLI interfaces with custom-built or
  otherwise unsupported test runners.
---

# \`raw\` profile for custom test runners

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

The `raw` CLI profile provides a low-level interface for interacting with Launchable. It is meant for use with custom-built test runners and requires additional integration steps in comparison to the native profiles built for each test runner.

Requirements:

1. You need to be able to programmatically create a list of tests you were going to run before running them
2. Your test runner needs to be able to accept a list of tests to run
3. You need to be able to convert your existing test results to JSON format, including creating Launchable-specific `testPath` identifiers for every test

{% hint style="warning" %}
The `raw` profile is an advanced feature. We strongly suggest you [contact us](https://www.launchableinc.com/support) if you plan to use it so that we can help!
{% endhint %}

## Recording test results

### Convert to JSON format

To submit test results with the `raw` profile, you'll need to convert your existing test results to JSON.

After you run tests, convert your test results to a JSON document using [this schema](https://github.com/launchableinc/cli/search?q=https%3A%2F%2Flaunchableinc.com%2Fschema%2FRecordTestInput). In particular, you'll need to create a `testPath` value for every test (see below).

```
## Example JSON document
{
  "testCases": [
     {
       "testPath": "file=login/test_a.py#class=class1#testcase=testcase899",
       "duration": 42,
       "status": "TEST_PASSED",
       "stdout": "This is stdout",
       "stderr": "This is stderr",
       "createdAt": "2021-10-05T12:34:00"
     }
  ]
}
```

### Constructing test paths

A `testPath` is a unique string that identifies a given test, such as

```
file=login/test_a.py#class=class1#testcase=testcase899
```

This example declares a hierarchy of three levels: a `testcase` belongs to a `class` which belongs to a `file` (path). Your hierarchy may be different, but you'll need to include enough hierarchy to uniquely identify every test.

When creating your `testPath` hierarchy, keep in mind that you'll also use this structure for subsetting tests. See (Subsetting hierarchy)\[#subsetting-hierarchy] for examples.

Finally, include relative file paths instead of absolute ones where possible.

{% hint style="warning" %}
**A note about file paths on Windows and Unix** If you include file paths in your `testPath` values and a given set of tests runs on both Unix and Windows, submit file paths with _either_ forward slashes or backslashes, but not both. If you submit a test with forward slashes in the file path and then submit the same test with backslashes in the file path, we will record two separate tests.
{% endhint %}

### Recording test results with the CLI

Then, pass that JSON document (e.g. `test-results/results.json`) to the Launchable CLI for submission:

```bash
launchable record tests --build <BUILD NAME> raw test-results/results.json
```

You can use `launchable inspect tests --test-session-id [TEST SESSION ID]` to inspect the list of test paths that were submitted.

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

### Subsetting your test runs

The high level flow for subsetting is:

1. Create file containing a list of all the tests in your test suite that you would _normally_ run
2. Pass that file to `launchable subset` with an optimization target
3. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
4. Use that file to tell your test runner to run only those tests

#### Subset input file format

The input file is a text file that contains test paths (e.g. `file=a.py#class=classA`), one per line Lines that start with a hash ('#') are considered comments and are ignored.

```
file=login/test_a.py#class=class1#testcase=testcase899
file=login/test_a.py#class=class2#testcase=testcase900
file=login/test_b.py#class=class3#testcase=testcase901
file=login/test_b.py#class=class3#testcase=testcase902
```

**Subsetting hierarchy**

One common scenario is that a test runner cannot subset tests at the same level of granularity used for reporting tests.

For example, if your tests are organized into a hierarchy of `file`s, `class`es, and `testcase`s, then your `testPath`s for recording tests will look like `file=<filePath>#class=<className>#testcase=<testcaseName>`, e.g.:

```
{
  "testCases": [
     {
       "testPath": "file=login/test_a.py#class=class1#testcase=testcase899",
       "duration": 10.051,
       "status": "TEST_PASSED",
     },
     {
       "testPath": "file=login/test_a.py#class=class2#testcase=testcase900",
       "duration": 13.625,
       "status": "TEST_FAILED",
     },
     {
       "testPath": "file=login/test_b.py#class=class3#testcase=testcase901",
       "duration": 14.823,
       "status": "TEST_PASSED",
     },
     {
       "testPath": "file=login/test_b.py#class=class3#testcase=testcase902",
       "duration": 29.784,
       "status": "TEST_FAILED",
     }
  ]
}
```

This creates four `testPath`s in Launchable:

```
file=login/test_a.py#class=class1#testcase=testcase899
file=login/test_a.py#class=class2#testcase=testcase900
file=login/test_b.py#class=class3#testcase=testcase901
file=login/test_b.py#class=class3#testcase=testcase902
```

However, perhaps your test runner can only subset at the `class` level, not the `testcase` level. In that case, send Launchable a list of `testPath`s that terminate at the `class` level, e.g.

```
file=login/test_a.py#class=class1
file=login/test_a.py#class=class2
file=login/test_b.py#class=class3
```

Launchable will then return a list of prioritized `class`es for you to run.

Similarly, if your test runner can only testcase at the `file` level, then simply submit a list of `testPath`s that terminate at the `file` level, e.g.:

```
file=login/test_a.py
file=login/test_b.py
```

Launchable will then return a list of prioritized `file`s for you to run.

#### Request a subset of tests to run with the CLI

Once you've created a subset input file, use the CLI to get a subset of the full list from Launchable:

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  raw \
  subset-input.txt > subset-output.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This will output `subset-output.txt` which contains a list of tests in the same format they were submitted. For example:

```
file=b.py#class=class4
file=b.py#class=class3
```

You can then process this file as needed for input into your test runner.
