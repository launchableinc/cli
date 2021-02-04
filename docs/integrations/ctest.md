# CTest

## Recording test results

Have CTest run tests and produce own format XML reports. Launchable CLI supports the CTest format. By default, this location is `Testing/{date}/Test.xml`.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
# `-T test` option output own format XML file
ctest -T test --no-compress-output

# record CTest result XML
launchable record tests --build <BUILD NAME> ctest Testing/**/Test.xml
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](always-run.md).

For more information and advanced options, run `launchable record tests ctest --help`

## Subsetting test execution

To select meaningful subset of tests, have CTest list your test cases \([documentation](https://cmake.org/cmake/help/latest/manual/ctest.1.html)\), then feed that into Launchable CLI:

```bash
# --show-only=json-v1 option outputs test list as JSON
ctest --show-only=json-v1 > test_list.json
launchable subset ... ctest test_list.json > launchable-subset.txt
```

The file will contain the subset of tests that should be run. Now invoke CTest by passing those as an argument:

```bash
# run the test
ctest -T test --no-compress-output -R $(cat launchable-subset.txt)
```

