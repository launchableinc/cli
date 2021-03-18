# CTest

## Recording builds

Launchable chooses which tests to run based on the changes contained in a **build**. To enable this, you need to send build information to Launchable.

Right before you run create a build in your CI script, invoke the Launchable CLI as follows:

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`.

## Subsetting tests

To select a meaningful subset of tests, have CTest list your test cases to a JSON file \([documentation](https://cmake.org/cmake/help/latest/manual/ctest.1.html)\), then feed that JSON into the Launchable CLI:

```bash
# --show-only=json-v1 option outputs test list as JSON
ctest --show-only=json-v1 > test_list.json
launchable subset \
    --build <BUILD NAME> \
    --target <TARGET> \
    ctest test_list.json > launchable-subset.txt
```

The file will contain the subset of tests that should be run. Now invoke CTest by passing those as an argument:

```bash
# run the tests
ctest -T test --no-compress-output -R $(cat launchable-subset.txt)
```

## Recording test results

Have CTest run tests and produce XML reports in its native format. Launchable CLI supports the CTest format; you don't need to convert to JUnit. By default, this location is `Testing/{date}/Test.xml`.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
# `-T test` option output own format XML file
ctest -T test --no-compress-output

# record CTest result XML
launchable record tests --build <BUILD NAME> ctest Testing/**/Test.xml
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests ctest --help`