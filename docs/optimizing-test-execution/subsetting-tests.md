# Subsetting tests

## Overview

After you've trained a model by [recording builds](../training-a-model/recording-builds.md) and [recording test results](../training-a-model/recording-test-results.md), we will contact you when your workspace's model is ready for use. Then you can run the `launchable subset` command to get a dynamic list of tests to run based on the changes in the `build` and the `target` you specify.

We will help you choose a target based on your requirements. In this example, we want to run 10% of the total test duration. We then pass that to a text file to be read later when tests run:

```bash
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    ...(test runner specific part)... > launchable-subset.txt
```

See the following sections for how to fill the `...(test runner specific part)...` in the above example:

* [Bazel](subsetting-tests.md#bazel)
* [CTest](subsetting-tests.md#ctest)
* [Cypress](subsetting-tests.md#cypress)
* [GoogleTest](subsetting-tests.md#googletest)
* [Go Test](subsetting-tests.md#go-test)
* [Gradle](subsetting-tests.md#gradle)
* [Maven](subsetting-tests.md#maven)
* [Minitest](subsetting-tests.md#minitest)
* [Nose](subsetting-tests.md#nose)

Not using any of these? Try the [generic file based test runner](subsetting-tests.md#generic-file-based-test-runner) option.

## Test runner integrations

### Bazel

To select meaningful subset of tests, first list up all the test targets you consider running, for example:

```bash
# list up all test targets in the whole workspace
bazel query 'tests(//...)'

# list up all test targets referenced from the aggregated smoke tests target
bazel query 'test(//foo:smoke_tests)'
```

You then pipe that into `launchable subset bazel` to obtain the subset of that target:

```bash
bazel query 'tests(//...)' | launchable subset \
    --build <BUILD NAME> \
    --target <TARGET> \
    bazel > launchable-subset.txt
```

You can now invoke Bazel with it:

```bash
bazel test $(cat launchable-subset.txt)
```

### CTest

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

### Cypress

To select a meaningful subset of tests, first pipe a list of all test files to the Launchable CLI \(`cypress/integration` is the [default directory](https://docs.cypress.io/guides/core-concepts/writing-and-organizing-tests.html#Test-files) for test files, so you'll need to change this if your tests live in a different directory\):

```bash
find ./cypress/integration | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  cypress > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
cypress run --spec "$(cat launchable-subset.txt)"
```

### GoogleTest

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

### Go Test

To select a meaningful subset of tests, have Go Test list your test cases \([upstream documentation](https://golang.org/cmd/go/#hdr-Testing_flags)\), then feed that into Launchable CLI:

```bash
go test -list ./... | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  go-test > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
go test -run $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report > report.xml
```

### Gradle

To select a meaningful subset of tests, provide the test source roots so the CLI can find all test classes:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  gradle project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The file will contain the subset of tests that should be run. Now invoke Gradle by passing those as an argument:

```bash
gradle test $(cat launchable-subset.txt)
```

### Maven

To select a meaningful subset of tests, provide the test source roots so the CLI can find all test classes:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  maven project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
mvn test -Dsurefire.includeFiles=launchable-subset.txt
```

### Minitest

To select meaningful subset of tests, feed all test Ruby source files to Launchable, like this:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  minitest test/**/*.rb > launchable-subset.txt
```

The file will contain the subset of test that should be run. You can now invoke minitest to run exactly those tests:

```bash
bundle exec rails test $(cat launchable-subset.txt)
```

### Nose

For subsetting, you need an additional flag called `--launchable-subset-target`, which specifies the percentage of subsetting in the total execution time.

```bash
# subset tests with Launchable
nosetests --launchable-subset --launchable-subset-target <TARGET>
```

### Generic file-based test runner

To obtain the appropriate subset of tests to run, start by enumerating test files that are considered for execution, then pipe that to `stdin` of `launchable subset` command.

The command will produce the names of the test files to be run to `stdout`, so you will then drive your test runner with this output.

```bash
find ./test -name '*.js' | 
launchable subset \
    --build <BUILD NAME> \
    --target <TARGET> \
    file > subset.txt

mocha $(< subset.txt)
```

