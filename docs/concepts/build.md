# Build

Every time you run automated tests, you're testing the behavior of some software. A **build** represents that software. Each time you send test results to Launchable, you record them against a specific build so that Launchable knows that you ran X tests against Y software with Z results.

Therefore, before you run your tests, you create a build using `launchable record build`.

## Build attributes

Every build has two primary attributes:

1. Its name (see [Choosing a value for \<BUILD NAME>](../sending-data-to-launchable/choosing-a-value-for-build-name.md))
2. Its relationships to commits in Git repositories

Let's expand on the second part: the relationship between builds and repositories.

When you record a build, you tell the CLI which source repo(s) and commit hash(es) the software was built from. For example, in the simplest case, the software is a single binary built from code in a single Git repository.

First, let's assume you've cloned the Git repository into the current directory (`.`) and that the relevant `HEAD` commit has already been checked out (e.g. `29932f39`). This is typically already available if you're building software and running tests on the same machine.

So, once you've done that, the command looks like this:

```
launchable record build --name $BUILD_NAME --source src=.
```

Running this command in your CI pipeline creates a build in your Launchable workspace. That build has a name (whatever `$BUILD_NAME` expanded to, e.g. `jenkins-myproject-123`) and one repository commit relation (name: `src`, commit: `29932f39`).

## Commit collection

By default, the `launchable record build` command _also_ runs the `launchable record commit` command.

This command collects the details of the changes in each commit in your repository (not just the `HEAD` commit) so that changes between builds can be compared later.

{% hint style="info" %}
By default, `launchable record build` runs `launchable record commit`, but these operations can be separated.
{% endhint %}

## More complex build/test pipelines

However, in many other cases, the software being tested might be a single binary built from several repos. Furthermore, the software being tested might be the combination of several services deployed to a single testing environment. The [Recording builds from multiple repositories](../sending-data-to-launchable/recording-builds-from-multiple-repositories.md) page outlines how to instrument your pipeline in these situations.
