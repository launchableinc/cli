# Gradle

## Recording builds

Launchable chooses which tests to run based on the changes contained in a **build**. To enable this, you need to send build information to Launchable.

Right before you create a build in your CI script, invoke the Launchable CLI as follows:

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`.

## Subsetting tests

To select a meaningful subset of tests, provide the test source roots so the CLI can find all test classes:

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  gradle project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with.

This command creates a `launchable-subset.txt` file that contains the subset of tests that should be run. You can now invoke Gradle to run exactly those tests:

```bash
gradle test $(cat launchable-subset.txt)
```

Note: The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
./gradlew testDebugUnitTest $(cat launchable-subset.txt)
```

Or:

```bash
./gradlew testReleaseUnitTest $(cat launchable-subset.txt)
```

## Recording test results

Have Gradle run tests and produce JUnit compatible reports. By default, report files are saved to `build/test-results/test/`, but that might be different depending on how your Gradle project is configured.

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories if you do multi-project build:

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle ./build/test-results/test/
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For a large project, a dedicated Gradle task to list up all report directories might be convenient. See [the upstream documentation](https://docs.gradle.org/current/userguide/java_testing.html#test_reporting) for more details and insights.

Alternatively, you can specify a glob pattern for directories or individual test report files \(this pattern might already be specified in your pipeline script for easy copy-pasting\):

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle **/build/**/TEST-*.xml
```

For more information and advanced options, run `launchable record tests gradle --help`