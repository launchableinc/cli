# Recording builds

Launchable decides which tests to prioritize based on the changes contained in a build**.** To enable this, you need to send build and commit information to Launchable.

Find the point in your CI process where source code gets converted into software that eventually get tested. This is typically called compilation, building, packaging, etc., using tools like Maven, make, grunt, etc.

{% hint style="info" %}
If you're using an interpreted language like Ruby or Python, record a build when you check out the repository as part of the build process.
{% endhint %}

Right before you produce a build in your CI script, invoke the Launchable CLI as follows.

With the `--name` option, you assign a unique identifier to this build. You will use this later when you [record test results](recording-test-results.md) to say "these tests ran against this build." See [Choosing a value for `<BUILD NAME>`](recording-builds.md#choosing-a-value-for-less-than-build-name-greater-than) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build. See [Data Privacy and Protection](../security/data-privacy-and-protection.md#specifics-on-the-data-sent-to-launchable) to learn more about what data we use from your repository.

In this example, the repository code is located in the current directory \(`.`\):

```bash
# record the build
launchable record build --name <BUILD NAME> --source .

# create the build
bundle install
```

Combined with earlier `launchable record build` invocations, this lets Launchable determine what’s changed for this particular build.

{% hint style="info" %}
If your software is built from multiple repositories, see [the example below](recording-builds.md#example-software-built-from-multiple-repositories).
{% endhint %}

## Choosing a value for `<BUILD NAME>`

Your CI process probably already relies on some identifier to distinguish different builds. Such an identifier might be called a build number, build ID, etc. Most CI systems automatically make these values available via built-in environment variables. This makes it easy to pass this value into `record build`:

| CI system | Suggested `<BUILD NAME>` | Docs |
| :--- | :--- | :--- |
| Azure DevOps Pipelines | `Build.BuildId` | [Link](https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables) |
| Bitbucket Pipelines | `BITBUCKET_BUILD_NUMBER` | [Link](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/) |
| CircleCI | `CIRCLE_BUILD_NUM` | [Link](https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables) |
| GitHub Actions | `GITHUB_RUN_ID` | [Link](https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables) |
| GitLab CI | `CI_JOB_ID` | [Link](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) |
| GoCD | `GO_PIPELINE_LABEL` | [Link](https://docs.gocd.org/current/faq/dev_use_current_revision_in_build.html#standard-gocd-environment-variables) |
| Jenkins | `BUILD_TAG` | [Link](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables) |
| Travis CI | `TRAVIS_BUILD_NUMBER` | [Link](https://docs.travis-ci.com/user/environment-variables/#default-environment-variables) |

Other examples:

* If your build produces an artifact or file that is later retrieved for testing, then `sha1sum` of the file would be a good build name as it is unique.
* If you are building a Docker image, its content hash can be used as the unique identifier of a build: `docker inspect -f "{{.Id}}"`.

{% hint style="warning" %}
If you only have one source code repository, it might tempting to use a Git commit hash \(or `git-describe`\) as the build name, but we discourage this.

It's not uncommon for teams to produce multiple builds from the same commit that are still considered different builds.
{% endhint %}

## Example: Software built from multiple repositories

If you produce a build by combining code from several repositories, invoke`launchable record build` with multiple `--source` options to denote them.

To differentiate them, provide a label for each repository in the form of `LABEL=PATH`:

```bash
# record the build
launchable record build --name <BUILD NAME> --source main=./main --source lib=./main/lib

# create the build
bundle install
```

{% hint style="info" %}
Note: `record build` automatically recognizes [Git submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), so there’s no need to explicitly declare them.
{% endhint %}

## Next steps

Now you can finish training a model by [recording test results](recording-test-results.md).

