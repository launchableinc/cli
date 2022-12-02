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

## Requesting and running a subset of tests

{% hint style="info" %}
If you're using [zero-input-subsetting](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting/ "mention"), scroll to this section.
{% endhint %}

### Normal approach

The high level flow for subsetting is:

1. Generate the full list of tests/test paths that _would have_ run during a normal session
2. Pass that list to `launchable subset` with an optimization target for the subset
3. `launchable subset` will create a subset from the full list and output that subset list to a text file
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

#### Maven + JUnit

```bash
mvn test -Dsurefire.includesFile=$PWD/launchable-subset.txt
```

{% hint style="warning" %}
If your build already depends on `surefire.includesFile`, or `<includes>/<includesFile>`, those and our subset will collide and not work as expected. [Contact us](https://www.launchableinc.com/support) to resolve this problem.
{% endhint %}

#### Maven + TestNG

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

#### Maven + JUnit & TestNG

If your multi-module project mixes JUnit and TestNG in different modules, follow "Maven + JUnit" guide above. The caveat is that modules using `testng.xml` to specify the tests to run will not work correctly because `testng.xml` and `surefire.includesFile` interferes.

### Zero Input Subsetting

If you're using [zero-input-subsetting](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting/ "mention") you'll get an exclusion list from Launchable. This list tells you which tests you can exclude.

The typical command to do this is:

```
launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  --get-tests-from-previous-sessions \
  --output-exclusion-rules \
  maven
  > launchable-exclusion-list.txt
```

* The `--build` option should use the same `<BUILD NAME>` value that you used before in `launchable record build`. See [#recording-builds](../../sending-data-to-launchable/#recording-builds "mention").
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [choosing-a-subset-optimization-target](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/choosing-a-subset-optimization-target/ "mention") for more info.

{% hint style="info" %}
See also [using-groups-to-split-subsets.md](../../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting/using-groups-to-split-subsets.md "mention"), which can split a large exclusion list into several lists, one per test group.
{% endhint %}

This creates a list of classes you can pass into Maven for exclusion:

```
mvn test -Dsurefire.excludesFile=$PWD/launchable-exclusion-list.txt
```

{% hint style="warning" %}
If your build already depends on `surefire.includesFile`, or `<includes>/<includesFile>`, those and our exclusion list will collide and not work as expected. [Contact us](https://www.launchableinc.com/support) to resolve this problem.
{% endhint %}
