---
description: This page outlines how to use Launchable's GitHub Actions.
---

# GitHub Actions

First, follow the instructions on [getting-started.md](../../getting-started.md "mention") to sign up and create a workspace for your test suite.

Then create an API key for your workspace in the **Settings** area _(click the cog ⚙️ icon in the sidebar)_. This authentication token lets the CLI talk to your Launchable workspace.

## [Launchable record build and test results action](https://github.com/marketplace/actions/record-build-and-test-results-action)

The Launchable record build and test results action enables you to integrate Launchable into your CI in simple way with less change. This action installs the [CLI](https://github.com/launchableinc/cli) and runs `launchable record build` and `launchable record test` to send data to Launchable so that the test results will be analyzed in [Launchable](https://www.launchableinc.com/) to improve your developer productivity.

### Example usage

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  LAUNCHABLE_TOKEN: ${{ secrets.LAUNCHABLE_TOKEN }}
  LAUNCHABLE_DEBUG: 1
  LAUNCHABLE_REPORT_ERROR: 1

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test
        run: <YOUR TEST COMMAND HERE>
      - name: Record
        uses: launchableinc/record-build-and-test-results-action@v1.0.0
        with:
          build_name: $GITHUB_RUN_ID
          test_runner: <YOUR TEST RUNNER HERE>
          report_path: <PATH TO TEST REPORT XML FILES>
        if: always()
```

| Test runner          | \`test\_runner\` value | Additional steps? |
| -------------------- | ---------------------- | ----------------- |
| Ant                  | `ant`                  |                   |
| Bazel                | `bazel`                |                   |
| Behave               | `behave`               | Yes               |
| CTest                | `ctest`                | Yes               |
| cucumber             | `cucumber`             | Yes               |
| Cypress              | `cypress`              |                   |
| GoogleTest           | `googletest`           | Yes               |
| Go Test              | `go-test`              | Yes               |
| Gradle               | `gradle`               |                   |
| Jest                 | `jest`                 | Yes               |
| Maven                | `maven`                |                   |
| minitest             | `minitest`             | Yes               |
| NUnit Console Runner | `nunit`                | Yes               |
| pytest               | `pytest`               | Yes               |
| Robot                | `robot`                |                   |
| RSpec                | `rspec`                | Yes               |

## Instructions for test runners/build tools

### Android Debug Bridge (adb)

Currently, the CLI doesn't have a `record tests` command for ADB. Use the command for [#gradle](github-actions.md#gradle "mention") instead.

### Ant

No special steps.

### Bazel



### Behave

First, in order to generate reports that Launchable can consume, add the `--junit` option to your existing `behave` command:

```bash
# run the tests however you normally do
behave --junit
```

### CTest

First, run your tests with `ctest -T test --no-compress-output`. These options ensure test results are written to the `Testing` directory.

### cucumber

First, run cucumber with the `-f junit` option, like this:

```bash
bundle exec cucumber -f junit -o reports
```

(If you use JSON, use the Launchable CLI instead.)

### Cypress



### GoogleTest

First, configure GoogleTest to produce JUnit compatible report files. See [their documentation](https://github.com/google/googletest/blob/master/docs/advanced.md#generating-an-xml-report) for how to do this. You'll end up with a command something like this:

```bash
# run the tests however you normally do
./my-test --gtest_output=xml:./report/my-test.xml
```

### Go Test

First, in order to generate reports that Launchable can consume, use [go-junit-report](https://github.com/jstemmer/go-junit-report) to generate a JUnit XML file after you run tests:

{% code overflow="wrap" %}
```bash
# install JUnit report formatter
go get -u github.com/jstemmer/go-junit-report

# run the tests however you normally do, then produce a JUnit XML file
go test -v ./... | go-junit-report -set-exit-code > report.xml
```
{% endcode %}

### Gradle

`**/build/**/TEST-*.xml`.

### Jest

First, in order to generate reports that Launchable can consume, use [jest-junit](https://www.npmjs.com/package/jest-junit) to generate a JUnit XML file after you run tests.

{% code overflow="wrap" %}
```bash
# install jest-junit reporter
npm install jest-junit --save-dev
# or
yarn add --dev jest-junit
```
{% endcode %}

You'll need to configure jest-junit to include file paths in reports.

You can do this using environment variables:

{% tabs %}
{% tab title="Using environment variables" %}
Recommended config:

```bash
export JEST_JUNIT_CLASSNAME="{classname}"
export JEST_JUNIT_TITLE="{title}"
export JEST_JUNIT_SUITE_NAME="{filepath}"
```

Minimum config:

```bash
export JEST_JUNIT_SUITE_NAME="{filepath}"
```
{% endtab %}

{% tab title="Using package.json" %}
Add the following lines to your `package.json`. The detail is the [jest-junit](https://www.npmjs.com/package/jest-junit) section.

Recommended config:

```json
// package.json
"jest-junit": {
  "suiteNameTemplate": "{filepath}",
  "classNameTemplate": "{classname}",
  "titleTemplate": "{title}"
}
```

Minimum config:

```json
// package.json
"jest-junit": {
  "suiteNameTemplate": "{filepath}"
}
```
{% endtab %}
{% endtabs %}

Then, run `jest` using jest-junit:

```bash
# run tests with jest-junit
jest --ci --reporters=default --reporters=jest-junit
```

### Maven

{% hint style="info" %}
Launchable supports test reports generated using [Surefire](https://maven.apache.org/surefire/maven-surefire-plugin/), the default report plugin for [Maven](https://maven.apache.org).
{% endhint %}

{% code overflow="wrap" %}
```bash
'./**/target/surefire-reports'
```
{% endcode %}

_Note: The invocation above relies on the CLI to expand GLOBs like `**`._

### minitest

First, use [minitest-ci](https://github.com/circleci/minitest-ci) to output test results to a file. If you already store your test results on your CI server, it may already be installed.

### NUnit Console Runner

{% hint style="info" %}
Launchable CLI accepts [NUnit3 style test report XML files](https://docs.nunit.org/articles/nunit/technical-notes/usage/XML-Formats.html) produced by NUnit.
{% endhint %}

### pytest

First, run tests with the `--junit-xml` option:

<pre class="language-bash"><code class="lang-bash"><strong>pytest --junit-xml=test-results/results.xml
</strong></code></pre>

{% hint style="warning" %}
pytest changed its default test report format from `xunit1` to `xunit2` in version 6. Unfortunately, the new `xunit2` format does not include file paths, which Launchable needs.

Thefore, if you are using pytest 6 or newer, you must also specify `junit_family=legacy` as the report format. See [Deprecations and Removals — pytest documentation](https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2) for instructions.
{% endhint %}

### Robot

```bash
output.xml
```

### RSpec

First, use [rspec\_junit\_formatter](https://github.com/sj26/rspec\_junit\_formatter) to output test results to a file in RSpec. If you already have a CI server storing your test results it may already be installed:

```bash
bundle exec rspec --format RspecJunitFormatter --out report/rspec.xml
```

