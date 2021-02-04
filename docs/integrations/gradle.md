# Gradle

## Recording test results

Have Gradle run tests and produce JUnit compatible reports. By default, this location is `build/test-results/test/` but that might be different depending on how your Gradle project is configured.

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories, for example if you do multi-project build:

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle ./build/test-results/test/
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](../resources/always-run.md).

For a large project, a dedicated Gradle task to list up all report directories might be convenient. See [the upstream documentation](https://docs.gradle.org/current/userguide/java_testing.html#test_reporting) for more details and insights.

Alternatively, you can specify a glob pattern for directories or individual test report files \(this pattern might already be specified in your pipeline script\):

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle **/build/**/TEST-*.xml
```

For more information and advanced options, run `launchable record tests gradle --help`

## Subsetting test execution

To select meaningful subset of tests, give the test source roots to find all test classes.

```bash
launchable subset ... gradle project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The file will contain the subset of tests that should be run. Now invoke Gradle by passing those as an argument:

```bash
gradle test $(cat launchable-subset.txt)
```

