# Zero Input Subsetting

Normally, when you run `launchable subset`, the Launchable CLI gathers the full list of tests on the client side and submits it with the subset request. (Highlighted in gray)

The subset request then returns a list of tests to **include** (i.e. run these tests):

<figure><img src="../../../../../.gitbook/assets/image (2) (1).png" alt=""><figcaption><p>Regular subsetting approach</p></figcaption></figure>

This strategy is problematic in some cases, which is why we've created a complementary approach called **Zero Input Subsetting**. With this approach, the CLI does not have to gather and submit the full list of tests. Instead, the server generates the full list of tests from the last 2 weeks of recorded sessions. And to ensure new tests are run, the CLI outputs exclusion rules instead of inclusion rules.

{% hint style="warning" %}
Zero Input Subsetting works better with some [#test-session-layouts](../../../../../concepts/test-session.md#test-session-layouts "mention") than others, so contact your Customer Success Manager before you start using this feature. We're here to help!
{% endhint %}

You can adopt this approach by adding two options to `launchable subset`:

* `--get-tests-from-previous-sessions`, and
* `--output-exclusion-rules`

The subset request then returns a list of tests to **exclude** (i.e. **don't** run these tests):

<figure><img src="../../../../../.gitbook/assets/image (1).png" alt=""><figcaption><p>Zero input subsetting</p></figcaption></figure>

The following CLI profiles/integrations support Zero Input Subsetting:

* [#gradle](./#gradle "mention")
* [#maven](./#maven "mention")
* [raw.md](../../../../../resources/integrations/raw.md "mention")

[Let us know](https://www.launchableinc.com/support) if you want to see support for another test runner!

Also see [using-groups-to-split-subsets.md](using-groups-to-split-subsets.md "mention") which expands this behavior.

## Instructions for test runners/build tools

### Gradle

First, you'll request an exclusion list from your full test suite. Then, you'll pass this list into Gradle.

#### Requesting an exclusion list

First, you need to add a snippet to your Gradle config to enable test exclusion via the Gradle command line:

```groovy
test {
    if (project.hasProperty('excludeTests')) {
        exclude project.property('excludeTests').split(',')
    }
}
```

Then, find the `gradle` command used to run tests in your CI script.

Before that command, run `launchable subset` to request an exclusion list. The subset and exclusion lists are generated from the union of tests recorded in the last 2 weeks.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules gradle > launchable-exclusion-list.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-exclusion-list.txt`. This file contains a list of test classes formatted for passing into Gradle, like this:

{% code title="launchable-exclusion-list.txt" %}
```
-PexcludeTests=com/example/FooTest.class,com/example/BarTest.class
```
{% endcode %}

#### Running a subset of tests

Then pass this file into your existing command, like shown below.

```bash
gradle test $(cat launchable-exclusion-list.txt)
# equivalent to gradle test -PexcludeTests=com/example/FooTest.class,com/example/BarTest.class
```

Note: If the exclusion list is very large, it may not be able to specify the list from the command directly. In that case, you can change the Gradle config to read from `launchable-exclusion-list.txt`.

Change the Gradle config as follows:

{% code overflow="wrap" %}
```groovy
test {
    if (project.hasProperty('excludeTestsTxt')) {
        exclude new File(project.property('excludeTestsTxt')).text.replaceFirst('-PexcludeTests=', '').trim().split(',')
    }
}
```
{% endcode %}

Then, specify the exclusion tests file from the command.

```bash
gradle test -PexcludeTestsTxt=$PWD/launchable-exclusion-list.txt
```

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
# request an exclusion list from all tests
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules gradle > launchable-exclusion-list.txt
# run tests, excluding deprioritized tests, leaving only the recommended subset
gradle test <OPTIONS> $(cat launchable-exclusion-list.txt)
```
{% endcode %}

### Gradle + TestNG

First, you'll request an exclusion list from your full test suite. Then, you'll pass this list into Gradle.

#### Requesting an exclusion list

First, find the `gradle` command used to run tests in your CI script.

Before that command, run `launchable subset` to request an exclusion list. The subset and exclusion lists are generated from the union of tests recorded in the last 2 weeks.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules gradle --bare > launchable-exclusion-list.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.
* Don't forget the `--bare` option after `gradle`!

This creates a file called `launchable-exclusion-list.txt`. This file contains a list of test classes formatted for passing into Gradle, like this:

{% code title="launchable-exclusion-list.txt" %}
```
com.example.FooTest
com.example.BarTest
...
```
{% endcode %}

#### Running a subset of tests

First, you need to add a dependency declaration to `build.gradle` so that the right tests get excluded when TestNG runs:

```
dependencies {
    ...
    testRuntime 'com.launchableinc:launchable-testng:1.2.1'
}
```

Then export the exclusion list file path as an environment variable before you run `mvn test`, like shown below.

```bash
export LAUNCHABLE_REST_FILE_PATH=$PWD/launchable-exclusion-list.txt
gradle test <OPTIONS>
```

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
# request an exclusion list from all tests
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> gradle --bare <PATH TO SOURCE> > launchable-exclusion-list.txt
# run tests, excluding deprioritized tests, leaving only the recommended subset
export LAUNCHABLE_REST_FILE_PATH=$PWD/launchable-exclusion-list.txt
gradle test <OPTIONS>
```
{% endcode %}

### Maven

First, you'll request an exclusion list from your full test suite. Then, you'll pass this list into Maven.

#### Requesting an exclusion list

Find the `mvn test` command used to run tests in your CI script.

Before that command, run `launchable subset` to request an exclusion list. The subset and exclusion lists are generated from the union of tests recorded in the last 2 weeks.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules maven > launchable-exclusion-list.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-exclusion-list.txt` that you can pass into Maven.

#### Running a subset of tests

To exclude deprioritized tests and only run the recommended subset, use the `-Dsurefire.excludesFile` option. For example:

{% code overflow="wrap" %}
```bash
mvn test <OPTIONS> -Dsurefire.excludesFile=$PWD/launchable-exclusion-list.txt
```
{% endcode %}

{% hint style="warning" %}
If your build already depends on `surefire.includesFile`, or `<includes>/<includesFile>`, those and our exclusion list will collide and not work as expected. [Contact us](https://www.launchableinc.com/support) to resolve this problem.
{% endhint %}

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
# get an exclusion list from the server
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules maven > launchable-exclusion-list.txt
# run tests, excluding deprioritized tests, leaving only the recommended subset
mvn test <OPTIONS> -Dsurefire.excludesFile=$PWD/launchable-exclusion-list.txt
```
{% endcode %}

### Maven + TestNG

First, you'll request an exclusion list from your full test suite. Then, you'll pass this list into Maven.

#### Requesting an exclusion list

Find the `mvn test` command used to run tests in your CI script.

Before that command, run `launchable subset` to request an exclusion list. The subset and exclusion lists are generated from the union of tests recorded in the last 2 weeks.

{% code overflow="wrap" %}
```bash
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules maven > launchable-exclusion-list.txt
```
{% endcode %}

* See [#options](./#options "mention") for how to set `<BUILD NAME>` and `<OPTIMIZATION TARGET OPTION>`.

This creates a file called `launchable-exclusion-list.txt` that you can pass into Maven.

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

Then export the exclusion list file path as an environment variable before you run `mvn test`, like shown below.

```bash
export LAUNCHABLE_REST_FILE_PATH=$PWD/launchable-exclusion-list.txt
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
# get an exclusion list from the server
launchable subset --build <BUILD NAME> <OPTIMIZATION TARGET OPTION> --get-tests-from-previous-sessions --output-exclusion-rules maven > launchable-exclusion-list.txt
# run tests, excluding deprioritized tests, leaving only the recommended subset
export LAUNCHABLE_REST_FILE_PATH=$PWD/launchable-exclusion-list.txt
mvn test <OPTIONS>
```
{% endcode %}
