# Subsetting with the Launchable CLI

## Overview

You use `launchable subset` to request a subset of tests from Launchable. You'll run this command before your normal test runner command. It generates a list of tests that you can pass into your test runner to run.

See [observing-subset-behavior](../../observing-subset-behavior/ "mention") if you want to test out subset behavior before running in production. Also see [zero-input-subsetting](zero-input-subsetting/ "mention") for an alternative subsetting interface that it useful in some scenarios.

## Options

{% hint style="warning" %}
**Read this section first!**
{% endhint %}

`launchable subset` takes various options:

1. high level options
2. test runner
3. test runner options

```
launchable subset <HIGH LEVEL OPTIONS> <TEST RUNNER> <TEST RUNNER OPTIONS>
```

`<TEST RUNNER>` is always a string representing the test runner in use, e.g. `maven`, `ant`, etc.

For brevity, the examples below do not include all high level options, so read this section and the [#subset](../../../../resources/cli-reference.md#subset "mention") section of the [cli-reference.md](../../../../resources/cli-reference.md "mention") before you continue. Test runner options are listed in each section.

### Required options

#### Optimization target

At minimum, you **must** specify an optimization target option, either

* `--confidence`
* `--time`
* `--target`

See [choosing-a-subset-optimization-target](../choosing-a-subset-optimization-target/ "mention") for more information.

#### Build or session identifier

The examples below include the high level `--build <BUILD NAME>` option, used for specifying the build to request tests for. This is the same build that you already created in order to record tests later. The subset command goes in between these.

**Before subsetting (simplified)**

```bash
# build process
launchable record build --name $BUILD_NAME <OPTIONS>
<build process>

# test process
<test process>
launchable record tests --build $BUILD_NAME <OPTIONS>
```

**After subsetting (simplified)**

```bash
# build process
launchable record build --name $BUILD_NAME <OPTIONS>
<build process>

# test process
launchable subset --build $BUILD_NAME <OPTIONS> # and related commands
<test process>
launchable record tests --build $BUILD_NAME <OPTIONS>
```

Note that if you already generate a test session manually (see [managing-complex-test-session-layouts.md](../../../../sending-data-to-launchable/using-the-launchable-cli/recording-test-results-with-the-launchable-cli/managing-complex-test-session-layouts.md "mention")) you'll want to use `--session` instead of `--build`.

## Instructions for test runners/build tools

{% hint style="info" %}
If you're not using any of these, use the [generic 'file-based' runner integration](../../../../resources/integrations/using-the-generic-file-based-runner-integration.md), the [`raw` profile for custom test runners](../../../../resources/integrations/raw.md), or [request a plugin](mailto:support@launchableinc.com?subject=Request%20a%20plugin).
{% endhint %}

### Android Debug Bridge (adb)

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into `adb` to run.

#### Requesting a subset of tests

Find the `adb` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `adb` command you normally use to run tests, and add the `-e log true` option. Then, output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
adb shell am instrument <OPTIONS> -e log true com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner > test_list.txt
```
{% endcode %}

This command outputs the full list of tests that would normally run (without actually running them) to a file called `test_list.txt`

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> adb > launchable-subset.txt
```
{% endcode %}

* &#x20;See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt`. This file contains a list of test classes formatted for passing into your normal `adb` command, shown next.

#### Running a subset of tests

Now you can run only the subset of tests by adding the `-e class $(cat launchable-subset.txt)` option to your normal `adb` command, like this:

{% code overflow="wrap" %}
```bash
adb shell am instrument <OPTIONS> -e class $(cat launchable-subset.txt) com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
adb shell am instrument <OPTIONS> com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list of tests in your suite
adb shell am instrument <OPTIONS> -e log true com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner > test_list.txt
# request a subset from the full list
cat test_list.txt | launchable subset  --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> adb > launchable-subset.txt
# run the results of the subset request
adb shell am instrument <OPTIONS> -e class $(cat launchable-subset.txt) com.yourdomain.test/androidx.test.runner.AndroidJUnitRunner
```
{% endcode %}

### Ant

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into your `build.xml` file to limit what Ant runs.

#### Requesting a subset of tests

First, find the `ant` command used to run tests in your CI script.

Before that command, add the `launchable subset` command to request a subset of tests from your full test suite:

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> ant <PATH TO SOURCE> > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Set `<PATH TO SOURCE>` to the path(s) containing your test files. The CLI will look in those path(s) and generate the full list of tests that would normally run. The subset service divides this full list into a subset list and a remainder list.

This creates a file called `launchable-subset.txt`. This file contains a list of test classes formatted for passing into your `build.xml` file, shown next.

#### Running a subset of tests

Separately, update your `build.xml` file to use `launchable-subset.txt`:

```markup
<project>
  …
  <target name="check-launchable">
    <available file="launchable-subset.txt" property="launchable"/>
  </target>

  <target name="junit" depends="jar,check-launchable">
    <mkdir dir="${report.dir}"/>
    <junit printsummary="yes">
      <classpath>
          <path refid="classpath"/>
          <path refid="application"/>
      </classpath>

      <formatter type="xml"/>

      <batchtest fork="yes" todir="${report.dir}">
        <fileset dir="${src.dir}" >
          <includesfile name="launchable-subset.txt" if="${launchable}" />
          <include name="**/*Test.java" unless="${launchable}" />
        </fileset>
      </batchtest>
    </junit>
  </target>
  …
</project>
```

Finally, you run tests command as normal, such as:

```bash
ant junit <OPTIONS>
```

### Bazel

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into Bazel to run.

#### Requesting a subset of tests

Find the `bazel` command used to run tests in your CI script. These commands will go _before_ that command.

First, run `bazel query` and output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
bazel query 'tests(//...)' > test_list.txt
```
{% endcode %}

This command outputs the full list of test targets that would normally run (without actually running them) to a file called `test_list.txt`. The subset service will divide this full list into a subset list and a remainder list.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> bazel > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt` that you can pass into Bazel.

#### Running a subset of tests

Simply append the list of tests to run to your existing command, such as:

```
bazel test $(cat launchable-subset.txt)
```

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
bazel test
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list
bazel query 'tests(//...)' > test_list.txt
# request a subset
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> bazel > launchable-subset.txt
# run the results of the subset request
bazel test $(cat launchable-subset.txt)
```
{% endcode %}

### Behave

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into Behave to run.

#### Requesting a subset of tests

Find the `behave` command used to run tests in your CI script. These commands will go _before_ that command.

First, run `find ./features/` and output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
find ./features/ > test_list.txt
```
{% endcode %}

This command creates the full list of test files that would normally run (without actually running them) to a file called `test_list.txt`. The subset service will divide this full list into a subset list and a remainder list.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> behave > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt` that you can pass into Behave.

#### Running a subset of tests

To run a subset, run `behave` with the `-i` option and pass in the subset list. For example:

```bash
behave <OPTIONS> -i "$(cat launchable-subset.txt)"
```

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
behave <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list
find ./features/ > test_list.txt
# request a subset
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> behave > launchable-subset.txt
# run the results of the subset request
behave <OPTIONS> -i "$(cat launchable-subset.txt)"
```
{% endcode %}

### CTest

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into CTest to run.

#### Requesting a subset of tests

Find the `ctest` command used to run tests in your CI script. These commands will go _before_ that command.

First, run `ctest` with the `--show-only` option and output the result to a JSON file. For example:

{% code overflow="wrap" %}
```bash
ctest <OPTIONS> --show-only=json-v1 > test_list.json
```
{% endcode %}

This command creates the full list of test files that would normally run (without actually running them) to a file called `test_list.json`. The subset service will divide this full list into a subset list and a remainder list.

Next, pass the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> --confidence <TARGET> ctest --output-regex-files --output-regex-files-dir=subsets test_list.json
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
*   The `--output-regex-files` instructs CLI to write the regular expression for

    the subset tests into the directory specified in `--output-regex-files-dir`.

This creates files under the `subsets` directory. `subset_N` are the files that contain regular expressions of the chosen subset of tests. If you use the `--rest` option, `rest_N` will be created containing the non-chosen tests.

#### Running a subset of tests

Then, run `ctest` for each subset output file:

```bash
for file in subset/subset_*; do
  ctest <OPTIONS> -T test --no-compress-output -R "$(cat "$file")"
done
```

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
ctest <OPTIONS> -T test --no-compress-output
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list that would normally run
ctest --show-only=json-v1 > test_list.json
# request a subset
launchable subset --build <BUILD NAME> --confidence <TARGET> ctest --output-regex-files --output-regex-files-dir=subsets test_list.json
# run the results of the subset request
for file in subset/subset_*; do
  ctest <OPTIONS> -T test --no-compress-output -R "$(cat "$file")"
done
```
{% endcode %}

### cucumber

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into cucumber to run.

#### Requesting a subset of tests

First, find the `bundle exec cucumber` command used to run tests in your CI script.

Before that command, add the `launchable subset` command to request a subset of tests from your full test suite:

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION>     cucumber <PATH TO .feature FILES> > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Set `<PATH TO .feature FILES>` to the glob expression representing your `.feature` files, e.g. `features/**/*.feature`. The CLI will look in those path(s) and generate the full list of tests that would normally run. The subset service divides this full list into a subset list and a remainder list.

This creates a file called `launchable-subset.txt`. This file contains a list of test files formatted for passing into cucumber, shown next.

#### Running a subset of tests

To run a subset, append the subset list to your `bundle exec cucumber` command. For example:

```bash
bundle exec cucumber -f junit -o reports <OPTIONS> $(cat launchable-subset.txt)
```

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
bundle exec cucumber -f junit -o reports <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# request a subset from all features that would normally run
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION>     ant <PATH TO .feature FILES> > launchable-subset.txt
# run the results of the subset request
bundle exec cucumber -f junit -o reports <OPTIONS> $(cat launchable-subset.txt)
```
{% endcode %}

### Cypress

Find the `cypress run` command used to run tests in your CI script. These commands will go _before_ that command.

First, run find `./cypress/integration -type f` and output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
find ./cypress/integration -type f > test_list.txt
```
{% endcode %}

This command creates the full list of test files that would normally run (without actually running them) to a file called `test_list.txt`. The subset service will divide this full list into a subset list and a remainder list.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> cypress > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt` that you can pass into Cypress.

#### Running a subset of tests

To run a subset, use the `--spec` option with the subset list text file. For example:

{% code overflow="wrap" %}
```bash
cypress run --reporter junit <OPTIONS> --spec "$(cat launchable-subset.txt)"
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
cypress run --reporter junit <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list that would normally run
find ./cypress/integration -type f > test_list.txt
# request a subset from all features that would normally run
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> cypress > launchable-subset.txt
# run the results of the subset request
cypress run --reporter junit <OPTIONS> --spec "$(cat launchable-subset.txt)"
```
{% endcode %}

### GoogleTest

Find the GoogleTest command used to run tests in your CI script. These commands will go _before_ that command.

First, invoke GoogleTest with the `--gtest_list_tests` option and output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
./my-test <OPTIONS> --gtest_list_tests > test_list.txt
```
{% endcode %}

This command outputs the full list of tests that would normally run (without actually running them) to a file called `test_list.txt`. The subset service will divide this full list into a subset list and a remainder list.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> googletest > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt` that you can pass into GoogleTest.

#### Running a subset of tests

Add the `--gtest_filter` option to your existing command, such as:

{% code overflow="wrap" %}
```bash
./my-test <OPTIONS> --gtest_filter="$(cat launchable-subset.txt)"
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
./my-test <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list
./my-test <OPTIONS> --gtest_list_tests > test_list.txt
# request a subset
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> googletest > launchable-subset.txt
# run the results of the subset request
./my-test <OPTIONS> --gtest_filter="$(cat launchable-subset.txt)"
```
{% endcode %}

### Go Test

Find the `go test` command used to run tests in your CI script. These commands will go _before_ that command.

First, invoke `go test` with the `--gtest_list_tests` option and output the result to a text file. For example:

First, duplicate the `go test` command you normally use to run tests, and add the `-list` option. Then, output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
go test <OPTIONS> -list="Test|Example" ./... > test_list.txt
```
{% endcode %}

This command outputs the full list of tests that would normally run (without actually running them) to a file called `test_list.txt`. The subset service will divide this full list into a subset list and a remainder list.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> go-test > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt` that you can pass into `go test`.

#### Running a subset of tests

Add the `-run` option to your existing command, such as:

{% code overflow="wrap" %}
```bash
go test <OPTIONS> -run $(cat launchable-subset.txt) ./... | go-junit-report > report.xml
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
go test <OPTIONS> ./...
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list
go test <OPTIONS> -list="Test|Example" . ./... > test_list.txt
# request a subset
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> go-test > launchable-subset.txt
# run the results of the subset request
go test <OPTIONS> -run $(cat launchable-subset.txt) ./... | go-junit-report > report.xml
```
{% endcode %}

### Gradle

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into Gradle.

#### Requesting a subset of tests

First, find the `gradle` command used to run tests in your CI script.

Before that command, add the `launchable subset` command to request a subset of tests from your full test suite:

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> gradle <PATH TO SOURCE> > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Set `<PATH TO SOURCE>` to the path(s) containing your test files, e.g. `project1/src/test/java project2/src/test/java`. The CLI will look in those path(s) and generate the full list of tests that would normally run. The subset service divides this full list into a subset list and a remainder list.

This creates a file called `launchable-subset.txt`. This file contains a list of test classes formatted for passing into Gradle, like this:

{% code title="launchable-subset.txt" %}
```
--tests MyTestClass1 --tests MyTestClass2 ...
```
{% endcode %}

#### Running a subset of tests

Then simply pass this file into your existing command, like shown below.

{% tabs %}
{% tab title="Gradle" %}
```bash
gradle test <OPTIONS> $(cat launchable-subset.txt)
# equivalent to gradle test <OPTIONS> --tests MyTestClass1 --tests MyTestClass2 ...
```
{% endtab %}

{% tab title="Gradle plugin for Android" %}
The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
./gradlew testDebugUnitTest <OPTIONS> $(cat launchable-subset.txt)
# or
./gradlew testReleaseUnitTest <OPTIONS> $(cat launchable-subset.txt)
```
{% endtab %}
{% endtabs %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
gradle test <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# request a subset from all tests
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> gradle <PATH TO SOURCE> > launchable-subset.txt
# run the results of the subset request
gradle test <OPTIONS> $(cat launchable-subset.txt)
```
{% endcode %}

### Gradle + TestNG

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into Gradle.

#### Requesting a subset of tests

First, find the `gradle` command used to run tests in your CI script.

Before that command, add the `launchable subset` command to request a subset of tests from your full test suite:

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> gradle --bare <PATH TO SOURCE> > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Set `<PATH TO SOURCE>` to the path(s) containing your test files, e.g. `project1/src/test/java project2/src/test/java`. The CLI will look in those path(s) and generate the full list of tests that would normally run. The subset service divides this full list into a subset list and a remainder list.
* Don't forget the `--bare` option after `gradle`!

This creates a file called `launchable-subset.txt`. This file contains a list of test classes formatted for passing into Gradle, like this:

{% code title="launchable-subset.txt" %}
```
com.example.FooTest
com.example.BarTest
...
```
{% endcode %}

#### Running a subset of tests

First, you need to add a dependency declaration to `build.gradle` so that the right subset of tests get executed when TestNG runs:

```
dependencies {
    ...
    testRuntime 'com.launchableinc:launchable-testng:1.2.1'
}
```

Then simply export the subset file path as an environment variable before you run `gradle test`, like shown below.

{% tabs %}
{% tab title="Gradle" %}
```bash
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
gradle test <OPTIONS>
```
{% endtab %}

{% tab title="Gradle plugin for Android" %}
The **Gradle plugin for Android** requires a different command, because the built-in `test` task does not support the `--tests` option. Use `testDebugUnitTest` or `testReleaseUnitTest` instead:

```bash
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
./gradlew testDebugUnitTest <OPTIONS> $(cat launchable-subset.txt)
# or
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
./gradlew testReleaseUnitTest <OPTIONS> $(cat launchable-subset.txt)
```
{% endtab %}
{% endtabs %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
gradle test <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# request a subset from all tests
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> gradle --bare <PATH TO SOURCE> > launchable-subset.txt
# run the results of the subset request using the `launchable-testng` plugin
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
gradle test <OPTIONS>
```
{% endcode %}

### Jest

Find the `jest` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `jest` command you normally use to run tests, and add the `--listTests` option. Then, output the result to a text file. For example:

{% code overflow="wrap" %}
```bash
jest <OPTIONS> --listTests > test_list.txt
```
{% endcode %}

This command creates the full list of test files that would normally run (without actually running them) to a file called `test_list.txt`. The subset service will divide this full list into a subset list and a remainder list.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --base $(pwd) cypress > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Don't forget the `--base $(pwd)` option before `cypress`.

This creates a file called `launchable-subset.txt` that you can pass into Jest.

#### Running a subset of tests

To run the subset, include the subset list after `jest`. For example:

{% code overflow="wrap" %}
```bash
jest <OPTIONS> $(cat launchable-subset.txt)
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
jest <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list that would normally run
jest <OPTIONS> --listTests > test_list.txt
# request a subset from all features that would normally run
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --base $(pwd) jest > launchable-subset.txt
# run the results of the subset request
jest <OPTIONS> $(cat launchable-subset.txt)
```
{% endcode %}

### Maven

Find the `mvn test` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `mvn test` command you normally use to run tests, but change `test` to `test-compile`. For example:

{% code overflow="wrap" %}
```bash
mvn test-compile <OPTIONS>
```
{% endcode %}

This command creates `.lst` files that list the test classes that would normally run (without actually running them). The subset service will combine these then divide this full list into a subset list and a remainder list.

Next, run `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> maven --test-compile-created-file <(find . -path '*/target/maven-status/maven-compiler-plugin/testCompile/default-testCompile/createdFiles.lst' -exec cat {} \;) > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* The `<(find...` section combines the `.lst` files across your projects into a single file for processing.

This creates a file called `launchable-subset.txt` that you can pass into Maven.

#### Running a subset of tests

To run the subset, use the `-Dsurefire.includesFile` option. For example:

{% code overflow="wrap" %}
```bash
mvn test <OPTIONS> -Dsurefire.includesFile=$PWD/launchable-subset.txt
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
mvn test <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list(s) that would normally run
mvn test-compile <OPTIONS>
# request a subset from all features that would normally run
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> maven --test-compile-created-file <(find . -path '*/target/maven-status/maven-compiler-plugin/testCompile/default-testCompile/createdFiles.lst' -exec cat {} \;) > launchable-subset.txt
# run the results of the subset request
mvn test <OPTIONS> -Dsurefire.includesFile=$PWD/launchable-subset.txt
```
{% endcode %}

### Maven + TestNG

Find the `mvn test` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `mvn test` command you normally use to run tests, but change `test` to `test-compile`. For example:

{% code overflow="wrap" %}
```bash
mvn test-compile <OPTIONS>
```
{% endcode %}

This command creates `.lst` files that list the test classes that would normally run (without actually running them). The subset service will combine these then divide this full list into a subset list and a remainder list.

Next, run `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> maven --test-compile-created-file <(find . -path '*/target/maven-status/maven-compiler-plugin/testCompile/default-testCompile/createdFiles.lst' -exec cat {} \;) > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* The `<(find...` section combines the `.lst` files across your projects into a single file for processing.

This creates a file called `launchable-subset.txt` that you can pass into Maven.

#### Running a subset of tests

First, modify your `pom.xml` so that it includes Launchable TestNG integration as a test scope dependency:

```xml
<dependency>
  <groupId>com.launchableinc</groupId>
  <artifactId>launchable-testng</artifactId>
  <version>1.2.1</version>
  <scope>test</scope>
</dependency>
```

Then simply export the subset file path as an environment variable before you run `mvn test`, like shown below.

```bash
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
mvn test <OPTIONS>
```

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
mvn test <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list of tests
mvn test-compile <OPTIONS>
# request a subset from all tests
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> maven --test-compile-created-file <(find . -path '*/target/maven-status/maven-compiler-plugin/testCompile/default-testCompile/createdFiles.lst' -exec cat {} \;) > launchable-subset.txt
# run the results of the subset request using the `launchable-testng` plugin
export LAUNCHABLE_SUBSET_FILE_PATH=$PWD/launchable-subset.txt
mvn test <OPTIONS>
```
{% endcode %}

### minitest

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into minitest to run.

#### Requesting a subset of tests

First, find the `bundle exec rails test` command used to run tests in your CI script.

Before that command, add the `launchable subset` command to request a subset of tests from your full test suite:

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> minitest <PATH TO .rb FILES> > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Set `<PATH TO .rb FILES>` to the glob expression representing your `.rb` test files, e.g. `test/**/*.rb`. The CLI will look in those path(s) and generate the full list of tests that would normally run. The subset service divides this full list into a subset list and a remainder list.

This creates a file called `launchable-subset.txt`. This file contains a list of tests formatted for passing into minitest.

#### Running a subset of tests

To run a subset, pass the subset list into `bundle exec rails test`. For example:

```bash
bundle exec rails test <OPTIONS> $(cat launchable-subset.txt)
```

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
bundle exec rails test <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# request a subset of your existing test suite
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> minitest <PATH TO .rb FILES> > launchable-subset.txt
# run the results of the subset request
bundle exec rails test <OPTIONS> $(cat launchable-subset.txt)
```
{% endcode %}

### NUnit Console Runner

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into `nunit3-console` to run.

#### Requesting a subset of tests

Find the `nunit3-console` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `nunit3-console` command you normally use to run tests, and add the `--explore` option. For example:

{% code overflow="wrap" %}
```bash
nunit3-console <OPTIONS> --explore=test_list.xml path/to/myassembly.dll
```
{% endcode %}

This command outputs the full list of tests that would normally run (without actually running them) to a file called `test_list.xml`.

Next, pass the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> nunit test_list.xml > launchable-subset.txt
```
{% endcode %}

* &#x20;See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt`. This file contains a list of test classes formatted for passing into your normal `adb` command, shown next.

Note: If you want to subset tests across multiple DLLs (for example, if multiple DLLs are combined into a logical 'suite'), you can run `nunit3-console --explore...` once for each DLL, then pass all the files into `launchable subset`, such as:

{% code overflow="wrap" %}
```bash
nunit3-console <OPTIONS> --explore=myassembly1.xml path/to/myassembly1.dll
nunit3-console <OPTIONS> --explore=myassembly2.xml path/to/myassembly2.dll
nunit3-console <OPTIONS> --explore=myassembly3.xml path/to/myassembly3.dll

launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> myassembly1.xml myassembly2.xml myassembly3.xml > launchable-subset.txt
```
{% endcode %}

#### Running a subset of tests

Now you can run only the subset of tests by adding the `--testlist` option to your normal `nunit3-console` command, like this:

{% code overflow="wrap" %}
```bash
nunit3-console <OPTIONS> --testlist=launchable-subset.txt path/to/myassembly.dll [path/to/myassembly2.dll] [path/to/myassembly3.dll]
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
nunit3-console <OPTIONS> path/to/myassembly.dll
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list of tests in your suite
nunit3-console <OPTIONS> --explore=test_list.xml path/to/myassembly.dll
# request a subset from the full list
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> nunit test_list.xml > launchable-subset.txt
# run the results of the subset request
nunit3-console <OPTIONS> --testlist=launchable-subset.txt path/to/myassembly.dll [path/to/myassembly2.dll] [path/to/myassembly3.dll]
```
{% endcode %}

### pytest

Find the `pytest` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `pytest` command you normally use to run tests, and add the `--collect-only` and `-q` options. Then output that to a file. For example:

{% code overflow="wrap" %}
```bash
pytest <OPTIONS> --collect-only -q > test_list.txt
```
{% endcode %}

This command outputs the full list of tests that would normally run (without actually running them) to a file called `test_list.txt`.

Next, pipe the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> pytest > launchable-subset.txt
```
{% endcode %}

* &#x20;See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt`. This file contains a list of tests formatted for passing into your normal `pytest` command, shown next.

#### Running a subset of tests

Now you can run only the subset of tests by passing the `launchable-subset.txt` file into `pytest`, like this:

{% code overflow="wrap" %}
```bash
pytest <OPTIONS> --junit-xml=test-results/subset.xml $(cat launchable-subset.txt)
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
pytest <OPTIONS> --junit-xml=test-results/subset.xml
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list of tests in your suite
pytest <OPTIONS> --collect-only -q > test_list.txt
# request a subset from the full list
cat test_list.txt | launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> pytest > launchable-subset.txt
# run the results of the subset request
pytest <OPTIONS> --junit-xml=test-results/subset.xml $(cat launchable-subset.txt)
```
{% endcode %}

### Robot

Find the `robot` command used to run tests in your CI script. These commands will go _before_ that command.

First, duplicate the `robot` command you normally use to run tests, and add the `--dryrun` and `-o` options. For example:

{% code overflow="wrap" %}
```bash
robot <OPTIONS> --dryrun -o test_list.xml
```
{% endcode %}

This command outputs the full list of tests that would normally run (without actually running them) to a file called `test_list.xml`.

Next, pass the file you just created into `launchable subset` to request a subset from the full list.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> robot test_list.xml > launchable-subset.txt
```
{% endcode %}

* &#x20;See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-subset.txt`. This file contains a list of tests formatted for passing into your normal `pytest` command, shown next.

#### Running a subset of tests

Now you can run only the subset of tests by passing the `launchable-subset.txt` file into `robot`, like this:

{% code overflow="wrap" %}
```bash
robot <OPTIONS> $(cat launchable-subset.txt) .
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
robot <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# generate the full list of tests in your suite
robot <OPTIONS> --dryrun -o test_list.xml
# request a subset from the full list
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> robot test_list.xml > launchable-subset.txt
# run the results of the subset request
robot <OPTIONS> $(cat launchable-subset.txt) .
```
{% endcode %}

### RSpec

First, you'll request a subset of tests from your full test suite. Then, you'll pass this list into minitest to run.

#### Requesting a subset of tests

First, find the `bundle exec rspec` command used to run tests in your CI script.

Before that command, add the `launchable subset` command to request a subset of tests from your full test suite:

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> rspec <PATH TO .rb FILES> > launchable-subset.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Set `<PATH TO .rb FILES>` to the glob expression representing your `.rb` test files, e.g. `spec/**/*_spec.rb`. The CLI will look in those path(s) and generate the full list of tests that would normally run. The subset service divides this full list into a subset list and a remainder list.

This creates a file called `launchable-subset.txt`. This file contains a list of tests formatted for passing into RSpec.

#### Running a subset of tests

To run a subset, pass the subset list into `bundle exec rails test`. For example:

{% code overflow="wrap" %}
```bash
bundle exec rspec $(cat launchable-subset.txt) --format d --format RspecJunitFormatter --out rspec.xml <OPTIONS>
```
{% endcode %}

#### Summary

In summary, here's the flow before:

{% code overflow="wrap" %}
```bash
# your normal command to run tests looks something like this
bundle exec rspec --format RspecJunitFormatter --out report/rspec.xml <OPTIONS>
```
{% endcode %}

And the flow after:

{% code overflow="wrap" lineNumbers="true" %}
```bash
# request a subset of your existing test suite
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> rspec <PATH TO .rb FILES> > launchable-subset.txt
# run the results of the subset request
bundle exec rspec $(cat launchable-subset.txt) --format d --format RspecJunitFormatter --out rspec.xml <OPTIONS>
```
{% endcode %}

## Other instructions

If you're not using any of these, see [raw.md](../../../../resources/integrations/raw.md "mention") or[using-the-generic-file-based-runner-integration.md](../../../../resources/integrations/using-the-generic-file-based-runner-integration.md "mention").

## Checking for integration issues

{% hint style="info" %}
Coming soon!
{% endhint %}
