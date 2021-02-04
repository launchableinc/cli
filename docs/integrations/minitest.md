# Minitest \(Ruby\)

## Recording test results

First, minitest has to be configured to produce JUnit compatible report files. We recommend [minitest-ci](https://github.com/circleci/minitest-ci).

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
bundle exec rails test

launchable record tests --build <BUILD NAME> minitest "$CIRCLE_TEST_REPORTS/reports"
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](../resources/always-run.md).

For more information and advanced options, run `launchable record tests minitest --help`

## Subsetting test execution

To select meaningful subset of tests, feed all test ruby source files to Launchable, like this:

```bash
launchable subset ...  minitest test/**/*.rb > launchable-subset.txt
```

The file will contain the subset of test that should be run. You can now invoke minitest to run exactly those tests:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

