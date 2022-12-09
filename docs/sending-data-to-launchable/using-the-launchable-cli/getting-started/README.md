# Getting started with the Launchable CLI

## Creating and setting your API key

First, create an API key in the **Settings** area _(click the cog ⚙️ icon in the sidebar)_. This authentication token lets the CLI talk to your Launchable workspace.

Then, make your API key available as the `LAUNCHABLE_TOKEN` environment variable in your CI process. How you do this depends on your CI system: _(If you're using a different CI system, check its documentation for a section about setting environment variables. Launchable works with any CI system.)_

| CI system              | Docs                                                                                                                                                                                                                                                                                         |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Azure DevOps Pipelines | [Link](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables?view=azure-devops\&tabs=yaml%2Cbatch#secret-variables)                                                                                                                                                      |
| Bitbucket Pipelines    | [Link](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/)                                                                                                                                                                                                            |
| CircleCI               | [Link](https://circleci.com/docs/2.0/env-vars/)                                                                                                                                                                                                                                              |
| GitHub Actions         | <p><a href="https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets">Link</a><br><br>Note: For public repositories using GitHub Actions, see <a data-mention href="using-the-cli-with-a-public-repository.md">using-the-cli-with-a-public-repository.md</a>.</p> |
| GitLab CI              | [Link](https://docs.gitlab.com/ee/ci/variables/)                                                                                                                                                                                                                                             |
| GoCD                   | [Link](https://docs.gocd.org/current/faq/dev\_use\_current\_revision\_in\_build.html#setting-variables-on-an-environment)                                                                                                                                                                    |
| Jenkins                | <p><a href="https://docs.cloudbees.com/docs/cloudbees-ci/latest/cloud-secure-guide/injecting-secrets">Link</a><br><br>Note: Create a global "secret text" to use in your job</p>                                                                                                             |
| Travis CI              | [Link](https://docs.travis-ci.com/user/environment-variables/)                                                                                                                                                                                                                               |

## Installing the Launchable CLI in your CI pipeline

The Launchable CLI is a Python3 package that you can install from [PyPI](https://pypi.org/project/launchable/). The CLI connects your build tool/test runner to Launchable.

You can install the CLI in your CI pipeline by adding the following command to the part of your CI script where you install dependencies. _(If your build and test process is split into different pipelines or machines, you'll need to do this in both places.)_

```bash
pip3 install --user --upgrade launchable~=1.0
```

{% hint style="warning" %}
The CLI requires both **Python 3.5+** _and_ **Java 8+**.
{% endhint %}

## Verifying connectivity

After setting your API key and installing the CLI, you can add `launchable verify || true` to your CI script to verify that everything is set up correctly. If successful, you should receive an output such as:

{% code overflow="wrap" %}
```bash
# We recommend including `|| true` after launchable verify so that the exit status from the command is always 0
$ launchable verify || true

Organization: <organization name>
Workspace: <workspace name>
Platform: <platform>
Python version: <version>
Java command: <command>
launchable version: <version>
Your CLI configuration is successfully verified 🎉
```
{% endcode %}

If you get an error, see [troubleshooting.md](../../../resources/troubleshooting.md "mention").
