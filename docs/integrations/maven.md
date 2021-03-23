# Maven

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  maven project1/src/test/java project2/src/test/java > launchable-subset.txt
```

```bash
mvn test -Dsurefire.includeFiles=launchable-subset.txt
```

```bash
launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  maven project1/src/test/java project2/src/test/java > launchable-subset.txt
```

```bash
mvn test -Dsurefire.includeFiles=launchable-subset.txt

mvn test -Dsurefire.includeFiles=launchable-remainder.txt
```

## Recording test results

The Surefire Plugin is default report plugin for [Apache Maven](https://maven.apache.org/). It's used during the test phase of the build lifecycle to execute the unit tests of an application. See [Maven Surefire Plugin – Introduction](https://maven.apache.org/surefire/maven-surefire-plugin/).

After running tests, point to the directory that contains all the generated test report XML files. You can specify multiple directories if you do multi-project build:

```bash
launchable record tests --build <BUILD NAME> maven ./project1/target/surefire-reports/ ./project2/target/surefire-reports/
```