# Page 1

First, follow the instructions on [getting-started.md](../../getting-started.md "mention") to sign up and create a workspace for your test suite.

## Create and set your API key

Then create an API key for your workspace in the **Settings** area _(click the cog ⚙️ icon in the sidebar)_. This authentication token lets the CLI talk to your Launchable workspace.

Add this value to your GitHub repository as an [encrypted secret](https://docs.github.com/en/actions/security-guides/encrypted-secrets) called `LAUNCHABLE_TOKEN`.

In the GitHub Actions YAML file where you run tests, expose this secret as an environment variable, like so:

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:

env:
  LAUNCHABLE_TOKEN: ${{ secrets.LAUNCHABLE_TOKEN }}

jobs:
  ...
```

You'll use it in the next step.

## Update your test runner

Then, locate the `step` where you run tests. It might look something like this:

```yaml
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test
        run: <YOUR TEST COMMAND HERE>
```

Depending on your test runner, you might need to modify your test runner command to ensure it creates test reports that Launchable accepts:

| Test runner         | Modifications                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Behave (Python)** | Run `behave` with the `--junit` option                                                                                                                                                                                                                                                                                                                                                                                                            |
| **CTest**           | Run `ctest` with the `-T test --no-compress-output` option                                                                                                                                                                                                                                                                                                                                                                                        |
| **cucumber**        | Run `cucumber` with the `-f junit` option                                                                                                                                                                                                                                                                                                                                                                                                         |
| **GoogleTest**      | Run with the `--gtest_output option`, e.g. `--gtest_output=xml:./report/report.xml`                                                                                                                                                                                                                                                                                                                                                               |
| **Go Test**         | <p>Use <a href="https://github.com/jstemmer/go-junit-report">go-junit-report</a> to generate a JUnit XML file after you run tests:</p><pre class="language-bash" data-overflow="wrap"><code class="lang-bash"># install JUnit report formatter
go get -u github.com/jstemmer/go-junit-report

# run the tests however you normally do, then produce a JUnit XML file
go test -v ./... | go-junit-report -set-exit-code > report.xml
</code></pre> |
| **Jest**            | Run `jest` using `jest-junit` as described here: [#jest](../using-the-launchable-cli/recording-test-results-with-the-launchable-cli/#jest "mention")                                                                                                                                                                                                                                                                                              |
| **minitest**        | Use [minitest-ci](https://github.com/circleci/minitest-ci) to output test results to a file                                                                                                                                                                                                                                                                                                                                                       |
| **pytest**          | <p>Run pytest with the <code>--junit-xml</code> option, e.g. <code>--junit-xml=test-results/results.xml</code><br><code></code><br><code></code>If you are using pytest 6 or newer, you must also specify <code>junit_family=legacy</code> (<a href="https://docs.pytest.org/en/latest/deprecations.html#junit-family-default-value-change-to-xunit2">docs</a>)</p>                                                                               |
| **RSpec**           | Use [rspec\_junit\_formatter](https://github.com/sj26/rspec\_junit\_formatter) to output test results to a file                                                                                                                                                                                                                                                                                                                                   |

## Add the Launchable action

After this, add the [Launchable record build and test results action](https://github.com/marketplace/actions/record-build-and-test-results-action) (lines 6-10 below):

<pre class="language-yaml" data-overflow="wrap" data-line-numbers><code class="lang-yaml"><strong>steps:
</strong>      - uses: actions/checkout@v2
      - name: Test
        run: &#x3C;YOUR TEST COMMAND HERE>
      - name: Record test results to Launchable workspace
        uses: launchableinc/record-build-and-test-results-action@v1.0.0
        with:
          test_runner: &#x3C;YOUR TEST RUNNER HERE>
          report_path: &#x3C;PATH TO TEST REPORT XML FILES>
        if: always()
</code></pre>

Then, based on your test runner, set `test_runner` and `report_path` values. **Note:** You may need to modify the `report_path` value to match your setup, so the values below are just suggestions.

| Test runner                    | Values                                                                                                                          |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| **Android Debug Bridge (adb)** | <pre class="language-yaml"><code class="lang-yaml">test_runner: gradle
report_path: **/build/**/TEST-*.xml
</code></pre>        |
| **Ant**                        | <pre class="language-yaml"><code class="lang-yaml">test_runner: ant
report_path: .
</code></pre>                                |
| **Bazel**                      | <pre class="language-yaml"><code class="lang-yaml">test_runner: bazel
report_path: .
</code></pre>                              |
| **Behave (Python)**            | <pre class="language-yaml"><code class="lang-yaml">test_runner: behave
report_path: ./reports/*.xml
</code></pre>               |
| **Ctest**                      | <pre class="language-yaml"><code class="lang-yaml">test_runner: ctest
report_path: Testing/**/Test.xml
</code></pre>            |
| **cucumber**                   | <pre class="language-yaml"><code class="lang-yaml">test_runner: cucumber
report_path: ./reports/**/*.xml
</code></pre>          |
| **Cypress**                    | <pre class="language-yaml"><code class="lang-yaml">test_runner: cypress
report_path: ./report/*.xml
</code></pre>               |
| **Go Test**                    | <pre class="language-yaml"><code class="lang-yaml">test_runner: go-test
report_path: report.xml
</code></pre>                   |
| **GoogleTest**                 | <pre class="language-yaml"><code class="lang-yaml">test_runner: googletest
report_path: ./report/*.xml
</code></pre>            |
| **Gradle**                     | <pre class="language-yaml"><code class="lang-yaml">test_runner: gradle
report_path: **/build/**/TEST-*.xml
</code></pre>        |
| **Jest**                       | <pre class="language-yaml"><code class="lang-yaml">test_runner: jest
report_path: *.xml
</code></pre>                           |
| **Maven**                      | <pre class="language-yaml"><code class="lang-yaml">test_runner: maven
report_path: './**/target/surefire-reports'
</code></pre> |
| **minitest**                   | <pre class="language-yaml"><code class="lang-yaml">test_runner: minitest
report_path: "**/reports"
</code></pre>                |
| **Nunit Console Runner**       | <pre class="language-yaml"><code class="lang-yaml">test_runner: nunit
report_path: TestResult.xml
</code></pre>                 |
| **pytest**                     | <pre class="language-yaml"><code class="lang-yaml">test_runner: pytest
report_path: ./test-results/
</code></pre>               |
| **Robot**                      | <pre class="language-yaml"><code class="lang-yaml">test_runner: robot
report_path: output.xml
</code></pre>                     |
| **RSpec**                      | <pre class="language-yaml"><code class="lang-yaml">test_runner: rspec
report_path: report/rspec.xml
</code></pre>               |

{% hint style="info" %}
If you're not using any of these, but your tool outputs JUnit XML report files, you can use:

```
test_runner: raw
report_path: <PATH TO YOUR REPORT FILES>
```
{% endhint %}

The GitHub Action performs three tasks:

1. Installs the Launchable [CLI](https://github.com/launchableinc/cli)
2. Records a [build.md](../../concepts/build.md "mention") (by running `launchable record build` under the hood)
3. Records test results to a [test-session.md](../../concepts/test-session.md "mention") (by running `launchable record tests` under the hood)

## Run tests

Once you've added the action, run the pipeline. If successful, you'll see Launchable output in your build logs, and you'll see your build and test session in the Launchable webapp at [app.launchableinc.com](https://app.launchableinc.com).

## Example

<pre class="language-yaml"><code class="lang-yaml">name: Maven test process

on:
  push:
    branches: [main]
  pull_request:

env:
  LAUNCHABLE_TOKEN: ${{ secrets.LAUNCHABLE_TOKEN }}
  LAUNCHABLE_DEBUG: 1
  LAUNCHABLE_REPORT_ERROR: 1

<strong>jobs:
</strong>  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test
        run: mvn test
      - name: Record test results to Launchable workspace
        uses: launchableinc/record-build-and-test-results-action@v1.0.0
        with:
          test_runner: maven
          report_path: './**/target/surefire-reports'
        if: always()
</code></pre>

