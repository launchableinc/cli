# Subset

A **subset** is a set of tests dynamically selected from a larger test suite using [predictive-test-selection](../features/predictive-test-selection/ "mention").

The term 'dynamically selected' refers to the fact that the tests returned in subsets change based on the request parameters.

## Properties

A subset is the output of a subset _request_ made using the `launchable subset` CLI command. You make a subset request every time you want to run a subset of tests in your CI pipeline:

![High level flow including a subset request](<../../.gitbook/assets/subsetting-diagram (2) (1).png>)

A subset request takes various inputs:

1. The [build.md](build.md "mention") being tested
2. A subset **optimization target**
3. The **test runner** in use
4. The **input test list**: the full list of tests that would normally run in a non-subset session (or "full run")

And outputs:

1. A **subset** list of tests formatted for your test runner
2. \[Optional] The **remainder** list of tests formatted for your test runner

### Build being tested

When you request a subset of tests to run in your CI process, you pass in the name of the [build.md](build.md "mention")you're testing:

```
launchable subset --build $BUILD_NAME [other options...]
```

This is important so that the Predictive Test Selection service can analyze the changes in the build and select tests appropriately.

### Optimization target

When you request a subset of tests to run in your CI process, you include an **optimization target**:

```
launchable subset \
    # one of:
    --target [PERCENTAGE]
    # or
    --confidence [PERCENTAGE]
    # or
    --time [STRING] \
    [other options...]
```

Launchable currently supports three optimization targets which you can read about here: [#choosing-an-optimization-target](../features/predictive-test-selection/#choosing-an-optimization-target "mention")

### Test runner

When you request a subset of tests, you include the name of the test runner you're going to run tests with. This value should be the same between `launchable subset` and `launchable record tests` commands.

The CLI uses this parameter to automatically adjust three things:

1. Input test list format
2. Subset altitude
3. Output test list format

#### Input test list format

The full list of tests you would normally run is a key input to any subset request. Launchable uses this list to create a subset of tests.

How this list is generated, formatted, and passed into the `launchable subset` depends on the test runner in use. In general, you don't have to worry about creating this list; the documentation for each test runner goes over the specific flow for your tool.

However, for completeness, we'll outline the various methods used across test runners:

1. Some test runners can generate a list of tests via a special command. The output of this command is then passed into `launchable subset`.
2. Other test runners don't provide that feature. In that case, you pass the _directory/directories_ containing your tests into `launchable subset`. The CLI then creates the list of tests by scanning those directories and identifying tests using pattern-matching.
3. Furthermore, some frameworks _can_ list individual tests, but they can only do so after test packages have been compiled. In this case it can be preferable to generate a list of higher-level packages instead of individual test cases. (This relates to the next section.)

#### Subset altitude and test items

To run a subset of tests, you pass the returned subset list into your test runner for execution.

Each test runner has its own option for specifying a list of tests to run, and these options allow for different 'altitudes' of filtering. For example, some test runners only let you pass in a list of _files_ to run, others support filtering by _class_, while some support filtering by _test case_ or _method_.

Based on the test runner specified in `launchable subset`, the CLI automatically outputs a list of tests using the hierarchy level supported by that test runner. We call these **test items**

{% hint style="info" %}
Another factor that impacts subset altitude is the ability of the test runner/CLI to _list_ tests at a low altitude. (See above section for more info)
{% endhint %}

For example, Maven supports filtering by class, so we say that Maven's _subset altitude_ is _class_. A test item for Maven is equivalent to a class. Test results captured using `launchable record tests` for Maven will include both class _and_ testcase identifiers, but the test item output of `launchable subset` will include a list of classes.

Here's the mapping for all test runners:

| Test runner                | Altitude |
| -------------------------- | -------- |
| Android Debug Bridge (adb) | Class    |
| Ant                        | Class    |
| Bazel                      | Target   |
| Behave                     | File     |
| Ctest                      | Testcase |
| cucumber                   | File     |
| Cypress                    | File     |
| Go Test                    | Testcase |
| GoogleTest                 | Testcase |
| Gradle                     | Class    |
| Jest                       | File     |
| Maven                      | Class    |
| minitest                   | File     |
| Nunit                      | Testcase |
| pytest                     | Testcase |
| Robot                      | Testcase |
| RSpec                      | File     |

The Launchable UI uses the term "test item" which represents the altitude shown above. For example, for Maven, "test items" map to **classes**, and so on, as mentioned above.

#### Output test list format

To run a subset of tests, you pass the returned subset list into your test runner for execution.

Each test runner has its own method or option for specifying a list of tests to run. For example, one test runner might expect a comma delimited list of tests, whereas another might expect a list separated by spaces, etc.

The CLI adjusts the output format automatically based on the test runner used in the request. In general, you don't need to worry about the output format because you'll pass it directly into your test runner per the documentation for your tool. But this does mean that the contents of subset files/outputs changes based on the test runner value.

### Input test list

As described above, the full list of tests you would normally run is a key input to any subset request. Launchable uses this list to create a subset of tests.

This list is important because it can change between requests due to

* new tests being added
* sub-suites being tested (see [#sub-suites-within-larger-test-suites](workspace.md#sub-suites-within-larger-test-suites "mention"))
* multiple test runner invocations per test session (see [#static-bins](test-session.md#static-bins "mention"))

In general, you don't have to worry about creating the input test list, but it's important to understand this concept because it relates to your optimization target. See[choosing-a-subset-optimization-target.md](../features/predictive-test-selection/choosing-a-subset-optimization-target.md "mention") for more on this.
