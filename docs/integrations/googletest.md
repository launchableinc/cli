# GoogleTest \(C++\)

## Recording test results

GoogleTest has to be configured to produce JUnit compatible report files. See [their documentation](https://github.com/google/googletest/blob/master/googletest/docs/advanced.md#generating-an-xml-report) for how to do this.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
./my-test --gtest_output=xml:./report/my-test.xml

launchable record tests --build <BUILD NAME> googletest ./report
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](../resources/always-run.md).

For more information and advanced options, run `launchable record tests googletest --help`

## Subsetting test execution

To select meaningful subset of tests, have GoogleTest list your test cases \([upstream documentation](https://github.com/google/googletest/blob/master/googletest/docs/advanced.md#listing-test-names)\), then feed that into Launchable CLI:

```bash
./my-test --gtest_list_tests | launchable subset ...  googletest > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
./my-test --gtest_filter="$(cat launchable-subset.txt)"
```

If you are only dealing with one test executable, you can also use `GTEST_FILTER` environment variable instead of the option. That might reduce the intrusion to your Makefile. See [upstream documentation](https://github.com/google/googletest/blob/master/googletest/docs/advanced.md#listing-test-names) for more details.

