# Getting started

## Overview

Implementing Launchable is a two phase process:

1. First, you **record a build** and **record test results** every time tests run in your CI pipeline. Launchable uses this data to build a machine learning model.
2. Then, you update your CI pipeline to use the trained model to optimize test execution by **subsetting tests**.

How does this look in practice? Here's an example. Let's say you have a simple CI script that builds and tests your Rails app:

```bash
## build step
# build software
bundle install

## test step
# run tests
bundle exec rails test
```

After you've added Launchable, this script would look like:

```bash
## install the Launchable CLI
pip3 install --user --upgrade launchable~=1.0

## build step

# before building software, send commit and build info
# to Launchable
launchable record build --name <BUILD NAME> [OPTIONS]

# build software as usual
bundle install

## test step
# ask Launchable which tests to run for this build
launchable subset --build <BUILD NAME> [OPTIONS] > subset.txt

# run those tests (note `-v $(cat tests.txt)`)
bundle exec rails test -v $(cat subset.txt)

# send test results to Launchable for this build
launchable record tests --build <BUILD NAME> [OPTIONS]
```

## Installing the CLI

The Launchable CLI is a Python3 package that can be installed from [PyPI](https://pypi.org/):

```bash
pip3 install --user --upgrade launchable~=1.0
```

You can install the CLI as a system package without `--user`, but this way you do not need root access. This is handy when you are adding this to your build script for your CI server.

The `--upgrade` flag makes sure to always install the latest `1.x` version.

## Setting your API key

You should have received an API key from us already \(if you haven’t, let us know\). This authentication token allows the CLI to talk to the Launchable cloud service.

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

You can run `launchable verify` in your script to test connectivity. If successful, you should receive an output like:

```bash
launchable verify  

Platform: macOS-11.1-x86_64-i386-64bit
Python version: 3.9.1
Java command: java
launchable version: 1.3.1
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [Troubleshooting](resources/troubleshooting.md).

It is always a good idea to run `launchable verify` in your build script, as this information is useful in case any problems arise. In that case, it is recommended to connect `|| true` so that the exit status is always `0`:

```bash
launchable verify || true
```

## Next steps

Now you can start training a model by [recording builds](training-a-model/recording-builds.md) and [recording test results](training-a-model/recording-test-results.md).

