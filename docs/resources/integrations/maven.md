---
description: This page outlines how the Launchable CLI interfaces with Maven.
---

# Maven

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started.md), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

{% hint style="info" %}
Launchable supports test reports generated using Surefire, the default report plugin for [Maven](https://maven.apache.org). See [Maven Surefire Plugin – Introduction](https://maven.apache.org/surefire/maven-surefire-plugin/).
{% endhint %}

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> maven './**/target/surefire-reports'
```

The invocation above relies on the CLI to expand GLOBs like `**`.

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

The high level flow for subsetting is:

1. Generate the full list of tests/test paths that _would have_ run during a normal session
2. Pass that list to `launchable subset` with an optimization target for the subset
3. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
4. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first create a list of all the tests you would _normally_ run using `mvn test-compile`. If you use any extra Maven options (such as `-Dsurefire.includesFile`, etc.), make sure to include them here so that the correct list of tests that _would_ have run is generated:

```bash
mvn test-compile
```

This process generates a file you can pass into `launchable subset`. This file is normally located at `target/maven-status/maven-compiler-plugin/testCompile/default-testCompile/createdFiles.lst` as shown below.

```bash
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  maven
  --test-compile-created-file <(find . -path '*/target/maven-status/maven-compiler-plugin/testCompile/default-testCompile/createdFiles.lst' -exec cat {} \;)
  > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../features/predictive-test-selection/) for more info.

The `launchable subset` command outputs a file called `launchable-subset.txt` that you can pass into Maven to run Launchable's selected subset. How you do that depends on what test framework you use.

### Maven + JUnit

```bash
mvn test -Dsurefire.includesFile=launchable-subset.txt
```

{% hint style="warning" %}
If your build is already depending on `surefire.includesFile`, or `<includes>/<includesFile>`, those and our subset will collide and will not work as expected. Contact us to resolve this problem.
{% endhint %}

### Maven + TestNG

Modify your `pom.xml` so that it includes Launchable TestNG integration as a test scope dependency:

```xml
<dependency>
  <groupId>com.launchableinc</groupId>
  <artifactId>launchable-testng</artifactId>
  <version>1.0.0</version>
  <scope>test</scope>
</dependency>
```

Pass the location of `launchable-subset.txt` as an environment variable. The abovementioned module will process this:

```bash
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
```

### Maven + JUnit & TestNG

If your multi-module project mixes JUnit and TestNG in different modules, follow "Maven + JUnit" guide above. The caveat is that modules using `testng.xml` to specify the tests to run will not work correctly because `testng.xml` and `surefire.includesFile` interferes.
