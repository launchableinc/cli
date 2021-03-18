# Bazel

## Recording builds

Launchable chooses which tests to run based on the changes contained in a **build**. To enable this, you need to send build information to Launchable.

Right before you run `bazel build` (or `bazel test` if you don't run `bazel build` separately) in your CI script, invoke the Launchable CLI as follows:

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`.

## Subsetting tests

First, ask Bazel for all the test targets you would normally run. For example:

```bash
# list up all test targets in the whole workspace
bazel query 'tests(//...)'
```

Then **pipe** those results into `launchable subset bazel` to get a subset of test targets to run from Launchable:

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    bazel > launchable-subset.txt
```

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with.

This creates a file called `launchable-subset.txt` you can pass to Bazel to run:

```bash
# run only the subset of test targets
bazel test $(cat launchable-subset.txt)
```

## Recording test results

After running tests, simply point to the Bazel workspace \(`.`\) to collect test results:

```bash
launchable record tests --build <BUILD NAME> bazel .
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../resources/always-run.md).
{% endhint %}

## Summary

After following these steps, your CI script should look something like this:

```bash
# tell Launchable about the changes in this build
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>

bazel build

# get a subset of test targets for this build from Launchable 
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    --rest launchable-remainder.txt
    bazel > launchable-subset.txt

# run only th esubset of test targets
bazel test $(cat launchable-subset.txt)

# record test results to train the model
launchable record tests --build <BUILD NAME> bazel .
```
