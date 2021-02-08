# Using 'sessions' to capture test reports from several machines

Some pipelines execute multiple test runs against a build in a single test session, outputting distinct test report\(s\) across several machines.

For example, one test session might include a Cypress run, a GoogleTest run, and a Bazel run, all executed separately, generating their own test report XML file\(s\) on separate machines.

These are all ostensibly part of a single test session, so it's desirable to treat them as such.

{% hint style="info" %}
This _may_ also be the case if you execute tests of a _single_ type across several parallel runs, but usually the test runner can combine reports from parallel runs for consumption from a single place.

If all the test reports for a session can be collected from a single machine, you don't need to use this method.
{% endhint %}

So, if you need to capture test reports from several machines, you can tell Launchable that they all relate to the same **test session** using the `launchable record session` command and the corresponding `--session` parameter _\(note: pseudocode\)_:

```bash
## build step

# before building software, send commit and build info
# to Launchable
launchable record build --build <BUILD NAME> [OPTIONS]

# build software the way you normally do, for example
bundle install

## test step

# before running tests, save a session token
# you'll use this token to group the test reports together later
launchable record session --build <BUILD NAME> --no-save-file > launchable-session.txt

    # start multiple test runs

        # machine 1

            # run tests
            bundle exec rails test

            # send test results to Launchable from machine 1
            # Note: You need to configure the line to always run whether test run succeeds/fails.
            #       See each integration page.
            launchable record tests --session $(cat launchable-session.txt) [OPTIONS]

        # machine 2

            # run tests
            bundle exec rails test

            # send test results to Launchable from machine 2
            # Note: You need to configure the line to always run whether test run succeeds/fails.
            #       See each integration page.
            launchable record tests --session $(cat launchable-session.txt) [OPTIONS]

        ## repeat as needed...

## finish multiple test runs
```

You can read more about `launchable record session` in the [CLI reference](cli-reference.md#record-session).

