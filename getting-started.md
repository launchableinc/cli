# Getting started

{% hint style="info" %}
Current as of:

* CLI version `1.1.2`
* Launchable version `054414f`
{% endhint %}

## Overview

Implementing Launchable is a two step process:

1. First, you send test results and build info to Launchable every time you run tests. Launchable uses this data to build a model.
2. Then, you updated your pipeline to use the trained model to optimize test execution.

At a very high level, the eventual integration looks something like:

```bash
## build step

# before building software, send commit and build info
# to Launchable
launchable record build ...

# build software the way you normally do, for example
bundle install

## test step

# initiate a Launchable session for this build
launchable record session ...

# ask Launchable which tests to run for this build
launchable subset ... > tests.txt

# run those tests, for example:
bundle exec rails test -v $(cat tests.txt) 

# send test results to Launchable for this session
launchable record tests ...
```

### Data model

Launchable optimizes test execution based on the new changes in a build being tested. Therefore, the data model is based around **builds** and **test sessions:**

**Builds** are inherently related to **commits** from one or several **repositories**. We compare commits between builds to identify changes.

A **test session** represents every time you run tests against a **build**. You can ask for optimized **tests** for that build during a test session, and you can submit **test reports** for that session to train the model.

## Installing the CLI

The Launchable CLI is a Python3 package that can be installed from [PyPI](https://pypi.org/):

```bash
pip3 install --user launchable~=1.1
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

Platform: macOS-10.15.7-x86_64-i386-64bit
Python version: 3.8.3
Java command: java
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
launchable record build ...

# build software the way you normally do, for example
bundle install

## test step

# initiate a Launchable session for this build
launchable record session ...

# run tests
bundle exec rails test

# send test results to Launchable for this session
launchable record tests ...
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
launchable record build --name $BUILD_NAME --source .

# create the build
bundle install
```

The `--source` option for both commands points to the local copy of the Git repository used to produce this build. See **Commit collection** above to learn more about how we use this.

With the `--name` option for `record build`, you assign a unique identifier to this build. You will use this later when you run tests. See [Naming builds](getting-started.md#naming-builds) for tips on choosing this value. This, combined with earlier `launchable record build` invocations, allows Launchable to determine what’s changed for this particular test session.

{% hint style="info" %}
If your software is built from multiple repositories, see [the example below](getting-started.md#example-software-built-from-multiple-repositories).
{% endhint %}

#### Naming builds

Your CI process probably already relies on some identifier to distinguish different builds. Such an identifier might be called a build number, build ID, etc. Most CI systems automatically make these values available via built-in environment variables. This makes it easy to pass this value into `record build`:

| CI system | Suggested variable | Documentation |
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
launchable record build --name $BUILD_NAME --source main=./main --source lib=./main/lib

# create the build
bundle install
```

{% hint style="info" %}
Note: `record build` automatically recognizes [Git submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), so there’s no need to explicitly declare them.
{% endhint %}

### Recording test results

First, you need to create a test session to record tests against. You can use `launchable record session` to do this. This command returns a value that you should store in a text file or as an environment variable for use later.

It's best to do this before you run tests, because later you'll add the `launchable optimize tests` command after it.

```bash
export LAUNCHABLE_SESSION=$(launchable record session --build $BUILD_NAME)
```

Then, after tests run, you send test reports to Launchable. How you do this depends on what test runners you use:

* [Bazel](integrations/bazel.md#record-tests)
* [GoogleTest](integrations/googletest.md#record-tests)
* [Go Test](integrations/go-test.md#record-tests)
* [Gradle](integrations/gradle.md#record-tests)
* [Minitest](integrations/minitest.md)
* [Nose](integrations/nose-python.md)

Not using any of these? Try the [generic file based test runner](integrations/file.md) option.

## Optimizing test execution

Your Launchable representative will contact you when your workspace's model is ready for use. Once it is, you can run the `launchable subset` command to get a dynamic list of tests to run from Launchable based on the changes in the `build` and the `target` you specify. In this example, we want to run 10% of tests, and we identify the full list of tests to run by inspecting Ruby files. We then pass that to a text file to be read later, when tests run:

```bash
launchable subset \
    --session "$LAUNCHABLE_SESSION" \
    --target 10% \
    ...(test runner specific part)... > launchable-subset.txt
```

See the following sections for how to fill the `...(test runner specific part)...` in the above example:

* [Bazel](integrations/bazel.md#subset)
* [GoogleTest](integrations/googletest.md#subset)
* [Go Test](integrations/go-test.md#subset)
* [Gradle](integrations/gradle.md#subset)
* [Minitest](integrations/minitest.md#subset)
* [Nose](integrations/nose-python.md#subset)
* [Generic file based test runner](integrations/file.md#subset)

If your test runner is not listed above, refer to [generic test optimization](https://github.com/launchableinc/mothership/tree/0988dad5518454683f59e045433d6ac42e32f49e/docs/integrations/generic.md#subset).

That makes the complete implementation, including capturing commits and builds:

```bash
# verify connectivity [optional]
launchable verify || true

# record the build along with commits
launchable record build --name $BUILD_NAME --source .

# compile
bundle install

# create a session for this build
export LAUNCHABLE_SESSION=$(launchable record session --build $BUILD_NAME)

# subset tests
launchable subset \
    --session "$LAUNCHABLE_SESSION" \
    --target 10% \
    minitest ./test \
    > launchable-subset.txt

# run the subset
bundle exec rails test -v $(cat launchable-subset.txt)

# send test reports
launchable record tests \
    --session "$LAUNCHABLE_SESSION" \
    minitest ./test/reports
```

## Troubleshooting

### Verification failure

#### Connectivity

If you need to interact with our API via static IPs, set the `LAUNCHABLE_BASE_URL` environment variable to `https://api-static.mercury.launchableinc.com`.

The IP for this hostname will be either `13.248.185.38` or `76.223.54.162`.

