# Getting started

## Overview

Implementing Launchable is a two phase process:

1. First, you send test results and build info to Launchable every time tests run in your CI pipeline. Launchable uses this data to build a model.
2. Then, you updated your CI pipeline to use the trained model to optimize test execution.

At a very high level, the eventual integration looks something like:

```bash
## build step

# before building software, send commit and build info
# to Launchable
launchable record build --name <BUILD NAME> [OPTIONS]

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

### Installing the CLI

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

If you get an error, see [Troubleshooting](resources/troubleshooting.md).

It is always a good idea to run `launchable verify` even for CI builds, as this information is useful in case of any problems. In that case, it is recommended to connect `|| true` so that the exit status is always `0`:

```bash
launchable verify || true
```

