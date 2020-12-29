# Bazel

## Recording test results

When you are running your tests with Bazel, simply point to the Bazel workspace to collect test results:

```text
# run the tests however you normally do
bazel test //...

launchable record tests bazel .
```

For more information and advanced options, run `launchable record tests bazel --help`

## Subset tests

To select meaningful subset of tests, first list up all the test targets you consider running, for example:

```text
# list up all test targets in the whole workspace
bazel query 'tests(//...)'

# list up all test targets referenced from the aggregated smoke tests target
bazel query 'test(//foo:smoke_tests)'
```

You feed that into `launchable subset bazel` to obtain the subset of those target:

```text
bazel query 'tests(//...)' |
launchable subset \
    --session "$LAUNCHABLE_SESSION" \
    --target 0.10 \
    > launchable-subset.txt
```

You can now invoke Bazel with it:

```text
bazel test $(cat launchable-subset.txt)
```

