# Getting started

## Overview

Implementing Launchable is a two phase process:

1. First, you **record a build** and **record test results** every time tests run in your CI pipeline. Launchable uses this data to build a machine learning model.
2. Then, you update your CI pipeline to use the trained model to optimize test execution by **subsetting tests**.

The Launchable CLI enables this integration.

## Installing the CLI

The Launchable CLI is a Python3 package that the CLI requires Python 3.5 or newer **and** Java 8 or newer.

You can install it from [PyPI](https://pypi.org/):

```bash
pip3 install --user --upgrade launchable~=1.0
```

The `--user` flag installs the package in the local account without needing root access. This is handy when you are adding this to your build script for your CI server.

The `--upgrade` flag makes sure to always install the latest `1.x` version.

## Setting your API key

You should have received an API key from us already \(if you haven’t, let us know\). This authentication token allows the CLI to talk to the Launchable service.

You’ll need to make this API key available as the `LAUNCHABLE_TOKEN` environment variable in the parts of your CI process that interact with Launchable. How you do this depends on your CI system:

<table>
  <thead>
    <tr>
      <th style="text-align:left">CI system</th>
      <th style="text-align:left">Docs</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left">Azure DevOps Pipelines</td>
      <td style="text-align:left"><a href="https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops&amp;tabs=yaml%2Cbatch#secret-variables">Set secret variables</a>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Bitbucket Pipelines</td>
      <td style="text-align:left"><a href="https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/">Variables and secrets</a>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">CircleCI</td>
      <td style="text-align:left"><a href="https://circleci.com/docs/2.0/env-vars/">Using Environment Variables</a>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">GitHub Actions</td>
      <td style="text-align:left"><a href="https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets">How to configure a secret</a>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">GitLab CI</td>
      <td style="text-align:left"><a href="https://docs.gitlab.com/ee/ci/variables/">GitLab CI/CD environment variables</a>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">GoCD</td>
      <td style="text-align:left"><a href="https://docs.gocd.org/current/faq/dev_use_current_revision_in_build.html#setting-variables-on-an-environment">Setting variables on an environment</a>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Jenkins</td>
      <td style="text-align:left">
        <p><a href="https://docs.cloudbees.com/docs/cloudbees-ci/latest/cloud-secure-guide/injecting-secrets">Injecting secrets into builds</a>
        </p>
        <p>(Create a global &quot;secret text&quot; to use in your job)</p>
      </td>
    </tr>
    <tr>
      <td style="text-align:left">Travis CI</td>
      <td style="text-align:left"><a href="https://docs.travis-ci.com/user/environment-variables/">Environment Variables</a>
      </td>
    </tr>
  </tbody>
</table>

## Verifying connectivity

After setting your API key, you can run `launchable verify` in your script to test connectivity. If successful, you should receive an output such as:

```bash
$ launchable verify

Organization: <organization>
Workspace: <workspace>
Platform: macOS-11.2.3-x86_64-i386-64bit
Python version: 3.9.2
Java command: java
launchable version: 1.8.0
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [Troubleshooting](resources/troubleshooting.md).

It is always a good idea to run `launchable verify` in your build script, as this information is useful in case any problems arise. In that case, it is recommended to connect `|| true` so that the exit status is always `0`:

```bash
launchable verify || true
```

## Next steps

Now that you've added the CLI to your pipeline, you can start optimizing your tests. The CLI natively integrates with the tools below. Click on the link to view instructions specific to your tool:

* [Bazel](integrations/bazel.md)
* [Behave](integrations/behave.md)
* [CTest](integrations/ctest.md)
* [Cypress](integrations/cypress.md)
* [GoogleTest](integrations/googletest.md)
* [Go Test](integrations/go-test.md)
* [Gradle](integrations/gradle.md)
* [Maven](integrations/maven.md)
* [Minitest](integrations/minitest.md)
* [Nose](integrations/nose.md)
* [Robot](https://github.com/launchableinc/cli/tree/7cf3c3a887e4fbd5990c688b38dcb6811b754d66/docs/integrations/robot.md)

Not using any of these? Try the [generic file based test runner](https://github.com/launchableinc/cli/tree/7cf3c3a887e4fbd5990c688b38dcb6811b754d66/docs/integrations/file.md) option.

{% tabs %}
{% tab title="Bazel" %}
```bash

```
{% endtab %}

{% tab title="Behave" %}
```bash

```
{% endtab %}

{% tab title="CTest" %}
```bash

```
{% endtab %}

{% tab title="Cypress" %}
```bash

```
{% endtab %}

{% tab title="Go Test" %}
```bash

```
{% endtab %}

{% tab title="GoogleTest" %}
```bash

```
{% endtab %}

{% tab title="Gradle" %}
```bash

```
{% endtab %}

{% tab title="Maven" %}
```bash

```
{% endtab %}

{% tab title="Minitest" %}
```bash

```
{% endtab %}

{% tab title="Nose" %}
```bash

```
{% endtab %}

{% tab title="Robot" %}
```bash

```
{% endtab %}

{% endtabs %}

