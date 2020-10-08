# Getting started

## API key

You should have received an API key from us already \(if you haven’t, let us know\). This is the authentication token that allows your build / test process to talk to Launchable service. You’ll need to make this API key available as the `LAUNCHABLE_TOKEN` environment variable in the parts of your CI process that interact with Launchable \(there are two, more later\).

How you do this depends on your CI system:

* **Jenkins**: See [how to use credentials](https://support.cloudbees.com/hc/en-us/articles/203802500-Injecting-Secrets-into-Jenkins-Build-Jobs). Easiest thing to do is to probably configure a global “secret text”, then insert that into your job.
* **GitHub Actions**: See [how to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets), which gets inserted as an environment variable

## Activate Launchable

Launchable will be a no-op until you set the `LAUNCHABLE` environment variable to on. The best place to do this is probably your CI system:

```text
export LAUNCHABLE=on

# build & test
make install test
```

## Integrating Launchable with your test runner

Find the point in your CI process where you want Launchable to optimize test execution. The way you invoke the test runner has to be modified, and how you do this depends on which test runner you are using:

* \*\*\*\*[**Python Nose**](integrations/nose-python.md)\*\*\*\*

## Install Launchable CLI

{% hint style="warning" %}
TODO: Add download
{% endhint %}

The Launchable CLI is a portable script you can download from here. You’ll need to make this script available in your `PATH` in your CI environment.

## Easy path

If your CI process is building & testing in one breath, then this is all you need!

More specifically, you have to meet all of the following criteria:

1. The software you are testing and the test code both reside in the same repository
2. You have that repository checked out in the workspace when you run tests
3. The software you are testing and the test code both come from the same commit

If all three apply to your situation, you’re done setting up Launchable. If not, read on.

## Expert path

If your CI process is more complicated, you may need to take a few more steps:

### Concepts

At the conceptual level, the process of integrating Launchable with your CI process involves telling Launchable three things:

1. Tell Launchable when you produce a new build, and what source code is used to produce it.
2. Tell Launchable when you are about to run tests on a build, and what tests you are about to run. This usually happens in the form of test runner plugin. Launchable will tell you back the best order & subset to run them.
3. Tell Launchable the results of each test execution.

### Recording a build

Find a point in your CI process where source code gets converted into the software that eventually get tested. This is typically called compilation, building, packaging, etc., using tools like Maven, make, grunt, etc.

Right before/after a build is produced, invoke the Launchable CLI as follows:

```text
launchable record build --name $BUILDID --source .
```

* With the `--name` option, you assign a unique identifier to this build, which you will use later when you run tests. More about how to choose the name later.
* The `--source` option points to the Git workspace used to produce this build.

### Choose a naming convention for builds

The time/place you do a build and the time/place you run tests can be far apart from each other. In this case, your CI process probably already relies on some identifier to distinguish different builds. Such identifier might be called a build number, build ID, etc. You can use those as the build name.

Some examples:

* If your build is producing a file, which is later retrieved by test, then `sha1sum` of the file would be a good build name, as it is unique.
* If you are building a Docker image, its content hash can be used as the unique identifier of SUT: `docker inspect -f "{{.Id}}"`. If your SUT is a file, use `sha1sum`.
* If you only have one source code repository, it is possible to use the git commit hash \(or git-describe\) as the build name, but we discourage you from doing this if you can avoid it. People do produce multiple builds from the same commit from time to time, and they are still generally considered different.

### Work with multiple git repositories

If you produce a build from multiple Git repositories, use multiple --source options to denote them. In order to differentiate those repositories, provide labels to different repositories in the form of `LABEL=PATH`:

{% hint style="info" %}
The `launchable record build` command automatically recognizes [Git submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), so there’s no need to explicitly declare submodules.
{% endhint %}

```text
launchable record build --name $BUILD_TAG --source main=./main --source lib=./main/lib
```

### Informing Launchable about the build you’re testing

Go back to the point where you integrated Launchable to your test runner. Prior to the test execution, set the `LAUNCHABLE_BUILD` environment variable to the `name` of the build you are testing. This, combined with earlier `launchable record build` invocations, allows Launchable to determine what’s changed for this particular test execution.

## How to…

### Verify that Launchable is working <a id="Verify-that-Launchable-is-working"></a>

If everything works correctly, you should see a log message printed out that mentions Launchable.

### Emergency kill switch <a id="Emergency-kill-switch"></a>

In the unlikely event of a catastrophic failure that needs immediate restoration of the service, simply remove the `LAUNCHABLE` environment variable or set it to `off`. Your test execution will continue as normal without any reordering.

