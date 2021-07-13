# Getting started

## Overview

{% hint style="info" %}
Before getting started, sign your team up for Launchable: [Sign up →](https://www.launchableinc.com/signup)

\(Launchable is free for small teams and open source projects. Otherwise, we offer a free 60-day trial\)
{% endhint %}

The Launchable CLI enables integration between your CI pipeline and Launchable. To get started,

1. install the CLI as part of your CI script,
2. set your Launchable API key, and
3. verify connectivity

Then follow the instructions for your test runner or build tool to send data to Launchable.

## Installing the CLI

The Launchable CLI is a Python3 package that you can install from [PyPI](https://pypi.org/project/launchable/).

{% hint style="warning" %}
Note that the CLI requires both **Python 3.5+** _and_ **Java 8+**.
{% endhint %}

You can install the CLI in your CI pipeline by adding this to the part of your CI script where you install dependencies:

```bash
pip3 install --user --upgrade launchable~=1.0
```

## Setting your API key

First, create an API key at [app.launchableinc.com](https://app.launchableinc.com). This authentication token allows the CLI to talk to Launchable.

Then, make this API key available as the `LAUNCHABLE_TOKEN` environment variable in your CI process. How you do this depends on your CI system:

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

After setting your API key, you can add `launchable verify || true` to your script to verify connectivity. If successful, you should receive an output such as:

```bash
$ launchable verify || true

Organization: <organization name>
Workspace: <workspace name>
Platform: macOS-11.4-x86_64-i386-64bit
Python version: 3.9.5
Java command: java
launchable version: 1.22.3
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [Troubleshooting](../resources/troubleshooting.md).

{% hint style="info" %}
We recommend including `|| true` so that the exit status from the command is always `0`.
{% endhint %}

## Next steps

Now that you've added the CLI to your pipeline, you can start [sending data to Launchable](../sending-data-to-launchable/) to analyze and optimize your test runs.

