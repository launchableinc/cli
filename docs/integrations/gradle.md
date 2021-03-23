# Gradle

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  gradle project1/src/test/java project2/src/test/java > launchable-subset.txt
```

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

For a large project, a dedicated Gradle task to list up all report directories might be convenient. See [the upstream documentation](https://docs.gradle.org/current/userguide/java_testing.html#test_reporting) for more details and insights.

Alternatively, you can specify a glob pattern for directories or individual test report files \(this pattern might already be specified in your pipeline script for easy copy-pasting\):

```bash
# run the tests however you normally do
gradle test ...

launchable record tests --build <BUILD NAME> gradle **/build/**/TEST-*.xml
```