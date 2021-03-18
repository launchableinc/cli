# Maven

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
  maven project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.

The `--target` option should be a percentage, such as `10%`. This creates a subset of the most useful test targets that will run in 10% of the full execution time. We'll suggest a value for you to start with.

This command creates a `launchable-subset.txt` file that contains the subset of tests that should be run. You can now invoke Maven to run exactly those tests:

```bash
mvn test -Dsurefire.includeFiles=launchable-subset.txt
```

## Recording test results

The Surefire Plugin is default report plugin for [Apache Maven](https://maven.apache.org/). It's used during the test phase of the build lifecycle to execute the unit tests of an application. See [Maven Surefire Plugin – Introduction](https://maven.apache.org/surefire/maven-surefire-plugin/).

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories if you do multi-project build:

```bash
# run the tests however you normally do, then produce a JUnit XML file
mvn test

launchable record tests --build <BUILD NAME> maven ./project1/target/surefire-reports/ ./project2/target/surefire-reports/
```

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests maven --help`