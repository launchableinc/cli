# Maven

## Recording test results

The Surefire Plugin is default report plugin for [Apache Maven](https://maven.apache.org/) and used during the test phase of the build lifecycle to execute the unit tests of an application. See [Maven Surefire Plugin – Introduction](https://maven.apache.org/surefire/maven-surefire-plugin/)

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories, for example if you do multi-project build:

```bash
# run the tests however you normally do, then produce a JUnit XML file
maven tests

launchable record tests --build <BUILD NAME> maven ./project1/target/surefire-reports/ ./project2/target/surefire-reports/
```

For more information and advanced options, run `launchable record tests maven --help`

## Subsetting test execution

To select a meaningful subset of tests, then feed that into Launchable CLI:

```bash
launchable subset --build <BUILD NAME>  project1/src/test/java project2/src/test/java > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
maven test -Dsurefire.includeFiles=launchable-subset.txt
```

