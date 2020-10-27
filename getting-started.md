# Getting started

## Quickstart

### Setting your API key

You should have received an API key from us already \(if you haven’t, let us know\). This authentication token allows your build and test process to talk to the Launchable service.

You’ll need to make this API key available as the `LAUNCHABLE_TOKEN` environment variable in the parts of your CI process that interact with Launchable. How you do this depends on your CI system:

* **Jenkins**: See [how to use credentials](https://support.cloudbees.com/hc/en-us/articles/203802500-Injecting-Secrets-into-Jenkins-Build-Jobs). Easiest thing to do is to probably configure a global “secret text”, then insert that into your job.
* **GitHub Actions**: See [how to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets), which gets inserted as an environment variable.

### Enabling Launchable

Launchable will be a no-op until you set the `LAUNCHABLE` environment variable to `on`. The best place to do this is probably your CI system:

```bash
# enable Launchable
export LAUNCHABLE=on

# build & test
make install test
```

### Adding Launchable to your test runner

Find the point in your CI process where you want Launchable to optimize test execution. The way you invoke the test runner has to be modified, and how you do this depends on which test runner you are using:

* [**Python Nose**](integrations/nose-python.md)

If everything works correctly, you should see a log message printed out when tests run that mentions Launchable. If not, read on.

## Advanced configuration

The quickstart setup from above assumes that the software you are testing is built and tested in a single step from a single repository. If this isn't the case, you'll need to record builds using the Launchable CLI.

The Launchable CLI is a Python3 package that can be installed with [PIP](https://pypi.org/):

```bash
pip3 install launchable
```

### Recording a build

To record a build, use `launchable record build` CLI command:

```bash
launchable record build --name $BUILDID --source .
```

* With the `--name` option, you assign a unique identifier to this build, which you will use later when you run tests. More about how to choose the name below.
* The `--source` option points to the local copy of the Git repository used to produce this build. See below if software is built from multiple repositories.

See below for usage examples.

#### Naming builds

Your CI process probably already relies on some identifier to distinguish different builds. Such identifier might be called a build number, build ID, etc. You can use those as the build name.

Some examples:

* If your build produces an artifact or file that is later retrieved for testing, then `sha1sum` of the file would be a good build name as it is unique.
* If you are building a Docker image, its content hash can be used as the unique identifier of a build: `docker inspect -f "{{.Id}}"`.

{% hint style="warning" %}
If you only have one source code repository, it is possible to use the Git commit hash \(or `git-describe`\) as the build name, but we discourage this where possible. People do produce multiple builds from the same commit from time to time, and they are still generally considered different.
{% endhint %}

#### Example: Separate build and test steps

The time/place you do a build and the time/place you run tests can be far apart from each other. In this case, you can use `launchable record build` to record the creation of the build for later reference when you invoke Launchable in the test process.

To do this, find a point in your CI process where source code gets converted into the software that eventually get tested. This is typically called compilation, building, packaging, etc., using tools like Maven, make, grunt, etc.

Right before a build is produced, invoke the Launchable CLI as follows. Remember to make your API key available as the `LAUNCHABLE_TOKEN` environment variable prior to invoking `launchable`:

```bash
# record the build
launchable record build --name $BUILDID --source .

# create the build
make bundle
```

Then, go back to the point where you integrated Launchable to your test runner. Prior to the test execution, set the `LAUNCHABLE_BUILD` environment variable to the `name` of the build you are testing. This, combined with earlier `launchable record build` invocations, allows Launchable to determine what’s changed for this particular test session.

```bash
# tell Launchable what's being tested
export LAUNCHABLE_BUILD=$BUILDID

# run tests
export LAUNCHABLE=ON
nosetests --launchable
```

#### Example: Software built from multiple repositories

If you produce a build from multiple Git repositories, invoke `launchable record build` with multiple `--source` options to denote them. In order to differentiate those repositories, provide labels to different repositories in the form of `LABEL=PATH`.

In this example, build and test happen in the same step, but the build is made from multiple repositories:

```bash
# create the build
make bundle

# record the build
launchable record build --name $BUILD_TAG --source main=./main --source lib=./main/lib

# tell Launchable what's being tested
export LAUNCHABLE_BUILD=$BUILDID

# run tests
export LAUNCHABLE=ON
nosetests --launchable
```

{% hint style="info" %}
Note: the `launchable record build` command automatically recognizes [Git submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), so there’s no need to explicitly declare submodules.
{% endhint %}

## How to…

### Verify that Launchable is working

If everything works correctly, you should see a log message printed out that mentions Launchable.

### Emergency kill switch

In the unlikely event of a catastrophic failure that needs immediate restoration of the service, simply remove the `LAUNCHABLE` environment variable or set it to `off`. Your test execution will continue as normal without any reordering.

