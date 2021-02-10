# Recording test results

## Overview

Once you've [recorded a build](recording-builds.md) and run tests against it, you need to send test reports to Launchable to train the model. How you do this depends on which test runner or build tool you use:

{% hint style="warning" %}
Some tools can stop test execution after a single test fails in order to provide quicker feedback to developers. This might be called "fast failure" or "fail fast" mode.

You'll need to disable this feature so that Launchable has enough test results to train an effective model.
{% endhint %}

* [Bazel](recording-test-results.md#bazel)
* [Cypress](recording-test-results.md#cypress)
* [CTest](recording-test-results.md#ctest)
* [GoogleTest](recording-test-results.md#googletest)
* [Go Test](recording-test-results.md#go-test)
* [Gradle](recording-test-results.md#gradle)
* [Maven](recording-test-results.md#maven)
* [Minitest](recording-test-results.md#minitest)
* [Nose](recording-test-results.md#nose)

Not using any of these? Try the [generic file based test runner](recording-test-results.md#generic-file-based-test-runner) option.

## Test runner integrations

### Bazel

When you are running your tests with Bazel, simply point to the Bazel workspace \(`.`\) to collect test results:

```bash
# run the tests however you normally do
bazel test //...

launchable record tests --build <BUILD NAME> bazel .
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests bazel --help`

### CTest

Have CTest run tests and produce XML reports in its native format. Launchable CLI supports the CTest format; you don't need to convert to JUnit. By default, this location is `Testing/{date}/Test.xml`.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
# `-T test` option output own format XML file
ctest -T test --no-compress-output

# record CTest result XML
launchable record tests --build <BUILD NAME> ctest Testing/**/Test.xml
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests ctest --help`

### Cypress

Cypress provides a JUnit report runner: see [Reporters \| Cypress Documentation](https://docs.cypress.io/guides/tooling/reporters.html).

After running tests, point to files that contains all the generated test report XML files:

```bash
# run the tests however you normally do, then produce a JUnit XML file
cypress run --reporter junit --reporter-options "mochaFile=report/test-output-[hash].xml"

launchable record tests --build <BUILD NAME> cypress ./report/*.xml
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests cypress --help`

### GoogleTest

GoogleTest has to be configured to produce JUnit compatible report files. See [their documentation](https://github.com/google/googletest/blob/master/googletest/docs/advanced.md#generating-an-xml-report) for how to do this.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
./my-test --gtest_output=xml:./report/my-test.xml

launchable record tests --build <BUILD NAME> googletest ./report
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests googletest --help`

### Go Test

Go Test does not natively produce JUnit compatible test report files, so you should use an extra tool such as [github.com/jstemmer/go-junit-report](https://github.com/jstemmer/go-junit-report) to convert them for use with Launchable.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# install JUnit report formatter
go get -u github.com/jstemmer/go-junit-report

# run the tests however you normally do, then produce a JUnit XML file
go test -v ./... | go-junit-report > report.xml

launchable record tests ... go-test .
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests go-test --help`

### Gradle

Have Gradle run tests and produce JUnit compatible reports. By default, report files are saved to `build/test-results/test/`, but that might be different depending on how your Gradle project is configured.

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories if you do multi-project build:

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle ./build/test-results/test/
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For a large project, a dedicated Gradle task to list up all report directories might be convenient. See [the upstream documentation](https://docs.gradle.org/current/userguide/java_testing.html#test_reporting) for more details and insights.

Alternatively, you can specify a glob pattern for directories or individual test report files \(this pattern might already be specified in your pipeline script for easy copy-pasting\):

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle **/build/**/TEST-*.xml
```

For more information and advanced options, run `launchable record tests gradle --help`

### Maven

The Surefire Plugin is default report plugin for [Apache Maven](https://maven.apache.org/). It's used during the test phase of the build lifecycle to execute the unit tests of an application. See [Maven Surefire Plugin – Introduction](https://maven.apache.org/surefire/maven-surefire-plugin/).

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories if you do multi-project build:

```bash
# run the tests however you normally do, then produce a JUnit XML file
mvn test

launchable record tests --build <BUILD NAME> maven ./project1/target/surefire-reports/ ./project2/target/surefire-reports/
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests maven --help`

### Minitest

First, minitest has to be configured to produce JUnit compatible report files. We recommend [minitest-ci](https://github.com/circleci/minitest-ci).

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
bundle exec rails test

launchable record tests --build <BUILD NAME> minitest "$CIRCLE_TEST_REPORTS/reports"
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests minitest --help`

### Nose

Install the Launchable plugin for Nose using PIP:

```bash
pip install nose-launchable
```

Then run tests with the Launchable plugin:

```text
nosetests --launchable
```

### Generic file-based test runner

The "file" test runner support is primarily designed to work with test runners not explicitly supported, including in-house custom test runners.

In order to work with Launchable through this integration mechanism, your test runner has to satisfy the following conditions:

* **File based**: your test runner accepts file names as an input of a test execution to execute just that specified set of tests.
* **File names in JUnit reports**: your test runner has to produce results of tests in the JUnit compatible format, with additional attributes that capture the file names of the tests that run. If not, see [dealing with custom test report format](../resources/convert-to-junit.md) for how to convert.

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

And it produces JUnit report files, where the name of the test file is captured, in this case the `file` attribute:

```bash
$ cat test-results.xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Mocha Tests" time="0.0000" tests="1" failures="0">
  <testsuite name="#indexOf()" file="/home/kohsuke/ws/foo.js" ...>
    <testcase  ... />
...
```

The rest of this section uses Mocha as an example.

To have Launchable capture the executed test results, run the `record tests file` command and specify file names of report files:

```bash
launchable record tests \
    --build <BUILD NAME> \
    --base . \
    file ./reports/*.xml
```

Note: When test reports contain absolute path names of test files, it prevents Launchable from seeing that `/home/kohsuke/ws/foo.js` from one test execution and `/home/john/src/foo.js` from another execution are actually the same test, so the `--base` option is used to relativize the test file names.

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

## Always record tests

The `launchable record tests` command must always run even if the test run succeeds or fails. However, some tools exit the build process as soon as the test process finishes, preventing this from happening. The way to fix this depends on your CI tool:

### Jenkins

Jenkins has [`post { always { ... } }`](https://www.jenkins.io/doc/book/pipeline/syntax/#post) option:

```text
pipeline {
  ...
  sh 'bundle exec rails test -v $(cat launchable-subset.txt)'
  ...
  post {
    always {
      sh 'launchable record tests <BUILD NAME> [OPTIONS]'
    }
  }
}
```

### CircleCI

CircleCI has [`when: always`](https://circleci.com/docs/2.0/configuration-reference/#the-when-attribute) option:

```yaml
- jobs:
  - test:
    ...
    - run:
        name: Run tests
        command: bundle exec rails test -v $(cat launchable-subset.txt)
    - run:
        name: Record test results
        command: launchable record tests <BUILD NAME> [OPTIONS]
        when: always
```

### Github Actions

GithubAction has [`if: ${{ always() }}`](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#always) option:

```yaml
jobs:
  test:
    steps:
      ...
      - name: Run tests
        run: bundle exec rails test -v $(cat launchable-subset.txt)
      - name: Record test result
        run: launchable record tests <BUILD NAME> [OPTIONS]
        if: always()
```

### Bash

If you run tests on your local or other CI, you can use `trap`:

```bash
function record() {
  launchable record tests <BUILD NAME> [OPTIONS]
}
# set a trap to send test results to Launchable for this build either tests succeed/fail
trap record EXIT SIGHUP

bundle exec rails test -v $(cat launchable-subset.txt)
```

## Next steps

Once you've started [recording builds](recording-builds.md) and test results for every test run, Launchable will start training a model. We will contact you by email when the model is ready to be used to [subset tests](../optimizing-test-execution/subsetting-tests.md).

