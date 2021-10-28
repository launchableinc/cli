# Using the generic file-based runner integration

{% hint style="info" %}
This is a reference page. See [Getting started](../getting-started/), [Sending data to Launchable](./), and [Subsetting your test runs](../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## About

The "file based" test runner integration is primarily designed to work with test runners that are not explicitly supported, such as custom test runners built in-house.

In order to work with Launchable through this integration mechanism, your test runner has to satisfy the following conditions:

* **File based**: your test runner accepts file names as an input of a test execution, to execute just those specified set of tests.
* **JUnit XML reports include file names/paths**: your test runner has to produce results of tests in a JUnit compatible format, with additional attributes that capture the **file names/paths** of the tests that run. If not, see [converting test reports to JUnit](converting-test-reports-to-junit-format.md).

For example, [Mocha](https://mochajs.org/#getting-started) is a test runner that meets those criteria. You write tests in JavaScript files:

```bash
$ cat foo.js
var assert = require('assert');
describe('Array', function() {
  describe('#indexOf()', function() {
    it('should return -1 when the value is not present', function() {
      assert.equal([1, 2, 3].indexOf(4), -1);
    });
  });
});
```

The Mocha test runner takes those files as arguments:

```bash
$ mocha --reporter mocha-junit-reporter foo.js
```

...and produces JUnit report files, where the name of the test file is captured, in this case, in the `file` attribute:

```bash
$ cat test-results.xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Mocha Tests" time="0.0000" tests="1" failures="0">
  <testsuite name="#indexOf()" file="/home/kohsuke/ws/foo.js" ...>
    <testcase  ... />
...
```

The rest of this document uses Mocha as an example.

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> file ./reports/*.xml
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of test files and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first pass the full list of test candidates to `launchable subset`. For example:

```bash
find ./test -name '*.js' | 
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    --rest launchable-remainder.txt \
    file > subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../actions/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
mocha $(< launchable-subset.txt)
```
