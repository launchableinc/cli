# Bazel
## Reordering
Suppose you have an invocation of Bazel to run tests:
```
bazel test //:integration-test
```

To use Launchable to attain the best test execution order, run `launchable bazel`:
```
launchable bazel test //:integration-tests
```

## Subsetting
To use Launchable to subset test executions to 10% by the test execution time, do as follows:
```
launchable bazel test --subset 10% //:integration-tests
```
Launchable computes the right 10% subset to invoke, then forks `bazel` with those targets to carry out
the execution.


## How to...
### Pass options to Bazel
Any options not recognized by Launchable gets passed as-is to Bazel, so you can
pass arbitrary Bazel options unmodified:
```
launchable bazel test --verbose_test_summary=false //:integration-tests
```
Use `--` to force Launchable to pass the rest of the options/arguments unmodified to Bazel
without further processing
```
launchable bazel test //:integration-tests -- --verbose_test_summary=false //more/target
```

### Invoking Bazel outside path
If you have the `bazel` executable outside your PATH, use the `--exec` option to specify where it is:

```
launchable bazel --exec=path/to/bazelisk test //:integration-tests
```
