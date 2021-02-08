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
pip3 install --user launchable~=1.0

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
pip3 install --user launchable~=1.0
```

It can be installed as a system package without `--user`, but this way you do not need the root access, which is handy when you are making this a part of the build script on your CI server.

## Setting your API key

You should have received an API key from us already \(if you haven’t, let us know\). This authentication token allows the CLI to talk to the Launchable service.

You’ll need to make this API key available as the `LAUNCHABLE_TOKEN` environment variable in the parts of your CI process that interact with Launchable. How you do this depends on your CI system:

* **Jenkins**: See [how to use credentials](https://support.cloudbees.com/hc/en-us/articles/203802500-Injecting-Secrets-into-Jenkins-Build-Jobs). The easiest thing to do is to configure a global “secret text," then insert that into your job.
* **CircleCI** See [Using Environment Variables](https://circleci.com/docs/2.0/env-vars/), which gets inserted as an environment variable.
* **GitHub Actions**: See [how to configure a secret](https://docs.github.com/en/free-pro-team@latest/actions/reference/encrypted-secrets), which gets inserted as an environment variable.

## Verifying connectivity

You can run `launchable verify` to test connectivity. If successful, you should receive an output like:

```bash
$ launchable verify  

Platform: macOS-11.1-x86_64-i386-64bit
Python version: 3.9.1
Java command: java
launchable version: 1.3.1
Your CLI configuration is successfully verified 🎉
```

If you get an error, see [Troubleshooting](resources/troubleshooting.md).

It is always a good idea to run `launchable verify` even for CI builds, as this information is useful in case of any problems. In that case, it is recommended to connect `|| true` so that the exit status is always `0`:

```bash
launchable verify || true
```

## Next steps

Now you can start training a model by [Recording builds](training-a-model/recording-builds.md) and [Recording test results](training-a-model/recording-test-results.md).

