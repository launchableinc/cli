# Gradle

## Recording test results

Have Gradle run tests and produce JUnit compatible reports. By default, this location
is `build/test-results/test/` but that might be different depending on how your Gradle project is configured.

After running tests, point to the directory that contains all the generated test report XML files.
You can specify multiple directories, for example if you do multi-project build:

```text
# run the tests however you normally do
gradle test ...

launchable record tests gradle ./build/test-results/test/
```

For a large project, a dedicated Gradle task to list up all report directories might be convenient.
See [the upstream documentation](https://docs.gradle.org/current/userguide/java_testing.html#test_reporting)
for more details and insights.

For more information and advanced options, run `launchable record tests gradle --help`

## Subset tests

To select meaningful subset of tests, give the test source roots to find all test classes.

```text
launchable subset ... gradle project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The file will contain the subset of tests that should be run.
Now invoke Gradle by passing those as an argument:

```text
gradle test $(cat launchable-subset.txt)
```
