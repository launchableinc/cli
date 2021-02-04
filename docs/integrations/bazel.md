# Bazel

## Recording test results

When you are running your tests with Bazel, simply point to the Bazel workspace to collect test results:

```bash
# run the tests however you normally do
bazel test //...

launchable record tests --build <BUILD NAME> bazel .
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](../resources/always-run.md).

For more information and advanced options, run `launchable record tests bazel --help`

## Subsetting test execution

To select meaningful subset of tests, first list up all the test targets you consider running, for example:

```bash
# list up all test targets in the whole workspace
bazel query 'tests(//...)'

# list up all test targets referenced from the aggregated smoke tests target
bazel query 'test(//foo:smoke_tests)'
```

You feed that into `launchable subset bazel` to obtain the subset of those target:

```bash
bazel query 'tests(//...)' |
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    bazel > launchable-subset.txt
```

You can now invoke Bazel with it:

```bash
bazel test $(cat launchable-subset.txt)
```

