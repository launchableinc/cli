# Getting started

## Overview

Implementing Launchable is a two step process:

1. First, you send test results and build info to Launchable every time tests run in your CI pipeline. Launchable uses this data to build a model.
2. Then, you updated your CI pipeline to use the trained model to optimize test execution.

At a very high level, the eventual integration looks something like:

```bash
## build step

# before building software, send commit and build info
# to Launchable
launchable record build --build <BUILD NAME> [OPTIONS]

# build software the way you normally do, for example
bundle install

## test step

# ask Launchable which tests to run for this build
launchable subset --build <BUILD NAME> [OPTIONS] > tests.txt

# run those tests, for example:
bundle exec rails test -v $(cat tests.txt)

# send test results to Launchable for this build
# Note: You need to configure the line to always run wheather test run succeeds/fails.
#       See each integration page.
launchable record tests --build <BUILD NAME> [OPTIONS]
```

### Data model

Launchable optimizes test execution based on the new changes in a build being tested. Therefore, the data model is based around **builds** and **test sessions:**

**Builds** are inherently related to **commits** from one or several **repositories**. We compare commits between builds to identify changes.

A **test session** represents every time you run tests against a **build**. You can ask for a subset of **tests** specifically for that build, and you can submit **test reports** for that build to train the model.

## Installing the CLI in your CI pipeline

The Launchable CLI is a Python3 package that can be installed from [PyPI](https://pypi.org/):

```bash
pip3 install --user launchable~=1.0
```

It can be installed as a system package without `--user`, but this way you do not need the root access, which is handy when you are making this a part of the build script on your CI server.

### Setting your API key

You should have received an API key from us already \(if you haven’t, let us know\). This authentication token allows the CLI to talk to the Launchable service.

You’ll need to make this API key available as the `LAUNCHABLE_TOKEN` environment variable in the parts of your CI process that interact with Launchable. How you do this depends on your CI system:

* **Jenkins**: See [how to use credentials](https://support.cloudbees.com/hc/en-us/articles/203802500-Injecting-Secrets-into-Jenkins-Build-Jobs). The easiest thing to do is to configure a global “secret text," then insert that into your job.
* **CircleCI** See [Using Environment Variables](https://circleci.com/docs/2.0/env-vars/), which gets inserted as an environment variable.
* **GitHub Actions**: See [how to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets), which gets inserted as an environment variable.

### Verifying connectivity

You can run `launchable verify` to test connectivity. If successful, you should receive an output like:

```bash
$ launchable verify  

Platform: macOS-11.1-x86_64-i386-64bit
Python version: 3.9.1
Java command: java
launchable version: 1.3.1
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [Troubleshooting](getting-started.md#troubleshooting).

It is always a good idea to run `launchable verify` even for CI builds, as this information is useful in case of any problems. In that case, it is recommended to connect `|| true` so that the exit status is always `0`:

```bash
launchable verify || true
```

## Training a model

First, you send test results and build info to Launchable every time you run tests. Launchable uses this data to build a model. When the model is trained, you'll update your pipeline again to [optimize test execution](getting-started.md#optimizing-test-execution).

To train the model, you need to implement **commit, build,** and **test report** collection.

At a high level, this looks like:

```bash
## build step

# before building software, send commit and build info
# to Launchable
launchable record build --build <BUILD NAME> [OPTIONS]

# build software the way you normally do, for example
bundle install

## test step

# run tests
bundle exec rails test

# send test results to Launchable for this build
# Note: You need to configure the line to always run wheather test run succeeds/fails.
#       See each integration page.
launchable record tests <BUILD NAME> [OPTIONS]
```

Keen eyes will notice that this is everything from the previous example **except** `launchable subset`, which we don't want to add until we're ready to actually subset tests.

### Recording builds

Launchable decides which tests to prioritize based on the changes contained in a build**.** To enable this, you need to send build and commit information to Launchable.

{% hint style="info" %}
**Commit collection**

Changes are contained in commits, so you need to record commits and builds alongside each other. Launchable collects commit information from the repositories that you specified using `--source`. We then compare that information with commits from previous builds to determine what's changed in the build currently being tested.

**We do not collect source code.** Only metadata about commits is captured, including:

* Commit hash, author info, committer info, timestamps, and message
* Names and paths of modified files
* Count of modified lines
{% endhint %}

Find the point in your CI process where source code gets converted into the software that eventually get tested. This is typically called compilation, building, packaging, etc., using tools like Maven, make, grunt, etc.

{% hint style="info" %}
If you're using an interpreted language like Ruby or Python, record a build when you check out the repository as part of the build process.
{% endhint %}

Right before a build is produced, invoke the Launchable CLI as follows. Remember to make your API key available as the `LAUNCHABLE_TOKEN` environment variable prior to invoking `launchable`. In this example, the repository code is located in the current directory:

```bash
launchable record build --name <BUILD NAME> --source .

# create the build
bundle install
```

The `--source` option for both commands points to the local copy of the Git repository used to produce this build. See **Commit collection** above to learn more about how we use this.

With the `--name` option for `record build`, you assign a unique identifier to this build. You will use this later when you run tests. See [Naming builds](getting-started.md#naming-builds) for tips on choosing this value. This, combined with earlier `launchable record build` invocations, allows Launchable to determine what’s changed for this particular build.

{% hint style="info" %}
If your software is built from multiple repositories, see [the example below](getting-started.md#example-software-built-from-multiple-repositories).
{% endhint %}

#### Choosing a value for `<BUILD NAME>`

Your CI process probably already relies on some identifier to distinguish different builds. Such an identifier might be called a build number, build ID, etc. Most CI systems automatically make these values available via built-in environment variables. This makes it easy to pass this value into `record build`:

| CI system | Suggested `<BUILD NAME>` | Documentation |
| :--- | :--- | :--- |
| Azure DevOps Pipelines | `Build.BuildId` | [https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables?view=azure-devops&tabs=yaml](https://docs.microsoft.com/en-us/azure/devops/pipelines/build/variables) |
| Bitbucket Pipelines | `BITBUCKET_BUILD_NUMBER` | [https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/](https://support.atlassian.com/bitbucket-cloud/docs/variables-and-secrets/) |
| CircleCI | `CIRCLE_BUILD_NUM` | [https://circleci.com/docs/2.0/env-vars/\#built-in-environment-variables](https://circleci.com/docs/2.0/env-vars/#built-in-environment-variables) |
| GitHub Actions | `GITHUB_RUN_ID` | [https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables\#default-environment-variables](https://docs.github.com/en/actions/configuring-and-managing-workflows/using-environment-variables#default-environment-variables) |
| GitLab CI | `CI_JOB_ID` | [https://docs.gitlab.com/ee/ci/variables/predefined\_variables.html](https://docs.gitlab.com/ee/ci/variables/predefined_variables.html) |
| GoCD | `GO_PIPELINE_LABEL` | [https://docs.gocd.org/current/faq/dev\_use\_current\_revision\_in\_build.html\#standard-gocd-environment-variables](https://docs.gocd.org/current/faq/dev_use_current_revision_in_build.html#standard-gocd-environment-variables) |
| Jenkins | `BUILD_TAG` | [https://www.jenkins.io/doc/book/pipeline/jenkinsfile/\#using-environment-variables](https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables) |
| Travis CI | `TRAVIS_BUILD_NUMBER` | [https://docs.travis-ci.com/user/environment-variables/\#default-environment-variables](https://docs.travis-ci.com/user/environment-variables/#default-environment-variables) |

Some examples:

* If your build produces an artifact or file that is later retrieved for testing, then `sha1sum` of the file would be a good build name as it is unique.
* If you are building a Docker image, its content hash can be used as the unique identifier of a build: `docker inspect -f "{{.Id}}"`.

{% hint style="warning" %}
If you only have one source code repository, it might tempting to use a Git commit hash \(or `git-describe`\) as the build name, but we discourage this.

It's not uncommon for teams to produce multiple builds from the same commit that are still considered different builds.
{% endhint %}

#### Example: Software built from multiple repositories

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

### Recording test results

Then, after tests run, you send test reports to Launchable. How you do this depends on what test runners you use:

* [Bazel](integrations/bazel.md#recording-test-results)
* [Cypress](integrations/cypress.md#recording-test-results)
* [GoogleTest](integrations/googletest.md#recording-test-results)
* [Go Test](integrations/go-test.md#recording-test-results)
* [Gradle](integrations/gradle.md#recording-test-results)
* [Maven](integrations/maven.md)
* [Minitest](integrations/minitest.md#recording-test-results)
* [Nose](integrations/nose-python.md)
* [CTest](integrations/ctest.md)

Not using any of these? Try the [generic file based test runner](integrations/file.md#recording-test-results) option.

## Subsetting test execution

Your Launchable representative will contact you when your workspace's model is ready for use. Once it is, you can run the `launchable subset` command to get a dynamic list of tests to run from Launchable based on the changes in the `build` and the `target` you specify. In this example, we want to run 10% of tests, and we identify the full list of tests to run by inspecting Ruby files. We then pass that to a text file to be read later, when tests run:

```bash
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    ...(test runner specific part)... > launchable-subset.txt
```

See the following sections for how to fill the `...(test runner specific part)...` in the above example:

* [Bazel](integrations/bazel.md#subsetting-test-execution)
* [Cypress](integrations/cypress.md#subsetting-test-execution)
* [GoogleTest](integrations/googletest.md#subsetting-test-execution)
* [Go Test](integrations/go-test.md#subsetting-test-execution)
* [Gradle](integrations/gradle.md#subsetting-test-execution)
* [Maven](integrations/maven.md)
* [Minitest](integrations/minitest.md#subsetting-test-execution)
* [Nose](integrations/nose-python.md#subsetting-test-execution)
* [CTest](integrations/ctest.md#subsetting-test-execution)

Not using any of these? Try the [generic file based test runner](integrations/file.md#subsetting-test-execution) option.

That makes the complete implementation, including capturing commits and builds:

```bash
# verify connectivity [optional]
launchable verify || true

# record the build along with commits
launchable record build --name <BUILD NAME> --source .

# compile
bundle install

# subset tests
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    minitest ./test \
    > launchable-subset.txt

# set trap to send test results to Launchable for this build either tests succeed/fail
function record() { \
    launchable record tests \
        --build <BUILD NAME> \
        minitest ./test/reports \
}
trap record EXIT SIGHUP

# run the subset
bundle exec rails test -v $(cat launchable-subset.txt)
```

## Troubleshooting

### Verification failure

#### Connectivity

If you need to interact with our API via static IPs, set the `LAUNCHABLE_BASE_URL` environment variable to `https://api-static.mercury.launchableinc.com`.

The IP for this hostname will be either `13.248.185.38` or `76.223.54.162`.

{% hint style="info" %}
This documentation is current as of CLI version `1.3.1`
{% endhint %}

