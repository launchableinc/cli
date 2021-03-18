# GoogleTest \(C++\)

## Recording builds

Launchable chooses which tests to run based on the changes contained in a **build**. To enable this, you need to send build information to Launchable.

Right before you run create a build in your CI script, invoke the Launchable CLI as follows:

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`.

## Subsetting tests

To select a meaningful subset of tests, have GoogleTest list your test cases \([upstream documentation](https://github.com/google/googletest/blob/master/googletest/docs/advanced.md#listing-test-names)\), then pipe that into Launchable CLI:

```bash
./my-test --gtest_list_tests | launchable subset  \
  --build <BUILD NAME> \
  --target <TARGET> \
  googletest > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
./my-test --gtest_filter="$(cat launchable-subset.txt)"
```

If you are only dealing with one test executable, you can also use `GTEST_FILTER` environment variable instead of the option. That might reduce the intrusion to your Makefile. See [upstream documentation](https://github.com/google/googletest/blob/master/googletest/docs/advanced.md#listing-test-names) for more details.

## Recording test results

GoogleTest has to be configured to produce JUnit compatible report files. See [their documentation](https://github.com/google/googletest/blob/master/docs/advanced.md#generating-an-xml-report) for how to do this.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
./my-test --gtest_output=xml:./report/my-test.xml

launchable record tests --build <BUILD NAME> googletest ./report
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests googletest --help`