# GoogleTest

```bash
./my-test --gtest_list_tests | launchable subset  \
  --build <BUILD NAME> \
  --target <TARGET> \
  googletest > launchable-subset.txt
```

```bash
./my-test --gtest_filter="$(cat launchable-subset.txt)"
```

```bash
./my-test --gtest_list_tests | launchable subset  \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  googletest > launchable-subset.txt
```

```bash
./my-test --gtest_filter="$(cat launchable-subset.txt)"

./my-test --gtest_filter="$(cat launchable-remainder.txt)"
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