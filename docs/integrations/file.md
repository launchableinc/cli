# Generic file based test runner

The "file" test runner support is primarily designed to work with test runners not explicitly supported, including in-house custom test runners.

In order to work with Launchable through this integration mechanism, your test runner has to satisfy the following conditions:

* **File based**: your test runner accepts file names as an input of a test execution, to execute just those

  specified set of tests.

* **File names in JUnit reports**: your test runner has to produce results of tests in

  the JUnit compatible format, with additional attributes that capture

  the file names of the tests that run. If not, see [Dealing with custom test report format](../resources/convert-to-junit.md)

  for how to convert.

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

Mocha test runner takes those files as arguments:

```bash
$ mocha --reporter mocha-junit-reporter foo.js
```

And it produces JUnit report files, where the name of the test file is captured, in this case the `file` attribute:

```bash
$ cat test-results.xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Mocha Tests" time="0.0000" tests="1" failures="0">
  <testsuite name="#indexOf()" file="/home/kohsuke/ws/foo.js" ...>
    <testcase  ... />
...
```

The rest of this document uses mocha as an example.

## Recording test results

To have Launchable capture the executed test results, run `record tests file` command and specify file names of report files:

```bash
launchable record tests \
    --build <BUILD NAME> \
    --base . \
    file ./reports/*.xml
```

When test reports contain absolute path names of test files, it prevents Launchable from seeing that `/home/kohsuke/ws/foo.js` from one test execution and `/home/john/src/foo.js` from another execution are actually the same test, so the `--base` option is used to relativize the test file names.

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](../resources/always-run.md).

## Subsetting test execution

To obtain the appropriate subset of tests to run, start by enumerating test files that are considered for execution, then pipe that to `stdin` of `launchable subset` command.

The command will produce the names of the test files to be run to `stdout`, so you will then drive your test runner with this output.

```bash
find ./test -name '*.js' | 
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    file > subset.txt

mocha $(< subset.txt)
```

