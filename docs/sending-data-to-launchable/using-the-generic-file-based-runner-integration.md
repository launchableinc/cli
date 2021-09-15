# Using the generic file-based runner integration

## Getting started

First, follow the steps in the [Getting started](../getting-started/) guide to install the Launchable CLI, set your API key, and verify your connection.

Then return to this page to complete the three steps of implementation:

1. Recording builds
2. Recording test results
3. Subsetting test execution

## About

The "file based" test runner integration is primarily designed to work with test runners that are not explicitly supported, such as custom test runners built in-house.

In order to work with Launchable through this integration mechanism, your test runner has to satisfy the following conditions:

* **File based**: your test runner accepts file names as an input of a test execution, to execute just those specified set of tests.
* **File names in JUnit reports**: your test runner has to produce results of tests in the JUnit compatible format, with additional attributes that capture the **file names** of the tests that run. If not, see [converting test reports to JUnit](converting-test-reports-to-junit-format.md).

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

Mocha test runner takes those files as arguments...

```bash
$ mocha --reporter mocha-junit-reporter foo.js
```

...produces JUnit report files, where the name of the test file is captured, in this case the `file` attribute:

```bash
$ cat test-results.xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Mocha Tests" time="0.0000" tests="1" failures="0">
  <testsuite name="#indexOf()" file="/home/kohsuke/ws/foo.js" ...>
    <testcase  ... />
...
```

The rest of this document uses Mocha as an example.

## Recording builds

Launchable selects tests based on the changes contained in a **build**. To send metadata about changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](choosing-a-value-for-build-name.md) for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`. You can include `--source` multiple times if your build is comprised of multiple repositories, e.g. `--source src=<PATH TO SOURCE` 1`> --source lib=<PATH TO SOURCE 2>`
  * See [Data privacy and protection](../policies/data-privacy-and-protection/) for more info about what information is collected.

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests \
    --build <BUILD NAME> \
    --base . \
    file ./reports/*.xml
```

* When test reports contain absolute path names of test files, it prevents Launchable from seeing that `/home/kohsuke/ws/foo.js` from one test execution and `/home/john/src/foo.js` from another execution are actually the same test, so the `--base` option is available to relativize the test file names.

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
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
mocha $(< launchable-subset.txt)
```
