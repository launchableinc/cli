# Getting started

## Overview

To get started,

1. sign up for Launchable
2. install the Launchable CLI as part of your CI script,
3. set your Launchable API key, and
4. verify connectivity

Then follow the instructions for your test runner or build tool to start [sending-data-to-launchable](sending-data-to-launchable/ "mention").

## Signing up for Launchable

Sign up at [app.launchableinc.com/signup](https://app.launchableinc.com/signup). You'll create a user account, an [organization.md](concepts/organization.md "mention") for your company or organization, and a [workspace.md](concepts/workspace.md "mention") for your test suite.

## Creating and setting your API key

Once you've created a [workspace.md](concepts/workspace.md "mention") for your test suite, create an API key in the **Settings** area. This authentication token lets the CLI talk to your Launchable workspace.

Then, make this API key available as the `LAUNCHABLE_TOKEN` environment variable in your CI process. How you do this depends on your CI system:

| CI system              | Docs                                                                                                                                                                                                 |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure DevOps Pipelines | [Set secret variables](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops\&tabs=yaml%2Cbatch#secret-variables)                                              |
| Bitbucket Pipelines    | [Variables and secrets](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)                                                                                                   |
| CircleCI               | [Using Environment Variables](https://circleci.com/docs/2.0/env-vars/)                                                                                                                               |
| GitHub Actions         | [How to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets)                                                                                     |
| GitLab CI              | [GitLab CI/CD environment variables](https://docs.gitlab.com/ee/ci/variables/)                                                                                                                       |
| GoCD                   | [Setting variables on an environment](https://docs.gocd.org/current/faq/dev\_use\_current\_revision\_in\_build.html#setting-variables-on-an-environment)                                             |
| Jenkins                | <p><a href="https://docs.cloudbees.com/docs/cloudbees-ci/latest/cloud-secure-guide/injecting-secrets">Injecting secrets into builds</a></p><p>(Create a global "secret text" to use in your job)</p> |
| Travis CI              | [Environment Variables](https://docs.travis-ci.com/user/environment-variables/)                                                                                                                      |

{% hint style="info" %}
Also see [using-the-cli-with-a-public-repository.md](sending-data-to-launchable/using-the-cli-with-a-public-repository.md "mention")
{% endhint %}

## Adding the Launchable CLI to your CI pipeline

The Launchable CLI is a Python3 package that you can install from [PyPI](https://pypi.org/project/launchable/). The CLI connects your build tool/test runner to Launchable.

{% hint style="info" %}
If you use pytest or nosetests, you don't need to use the Launchable CLI! We offer native plugins for those test runners. Check out the [pytest.md](resources/integrations/pytest.md "mention") and [nose.md](resources/integrations/nose.md "mention") pages for more info.
{% endhint %}

You can install the CLI in your CI pipeline by adding this to the part of your CI script where you install dependencies. (If your build and test process is split into different pipelines or machines, you'll need to do this in both places.)

```bash
pip3 install --user --upgrade launchable~=1.0
```

{% hint style="warning" %}
The CLI requires both **Python 3.5+** _and_ **Java 8+**.
{% endhint %}

## Verifying connectivity

After setting your API key and installing the CLI, you can add `launchable verify || true` to your CI script to verify that everything is set up right. If successful, you should receive an output such as:

```bash
$ launchable verify || true

Organization: <organization name>
Workspace: <workspace name>
Platform: <platform>
Python version: <version>
Java command: <command>
launchable version: <version>
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [troubleshooting.md](resources/troubleshooting.md "mention").

{% hint style="info" %}
We recommend including `|| true` after `launchable verify` so that the exit status from the command is always `0`.
{% endhint %}

## Next steps

Now that you've connected your Launchable workspace to your CI pipeline, you can start [sending-data-to-launchable](sending-data-to-launchable/ "mention") to take advantage of Launchable's features.
