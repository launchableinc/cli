# Converting test reports to JUnit format

## Dealing with custom test report format

Launchable uses the so-called JUnit report format in the `launchable record tests` command. This is the de facto test report format that is supported by many build/test/CI tools. However, if yours does not, we need you to write a little program to convert your formats into the JUnit report format.

[This page](https://llg.cubic.org/docs/junit/) and [this page](https://help.catchsoftware.com/display/ET/JUnit+Format) are probably the best annotated examples of the JUnit report format. Launchable only looks at the following information:

### Must have

* `<testsuites>`, `<testsuite>`, `<testcase>` are the structural elements that matter. Their `name`, `classname` attributes are used to identify test names
* For a failed/errored/skipped test case, `<testcase>` element must have nested `<failure>`, `<error>`, or `<skipped>` child element
* While not documented in the referenced pages, `file` or `filepath` attributes on structural elements that point to the test source file path are a must for file-based test runner support, most notably the [file](converting-test-reports-to-junit-format.md) mode, which is most likely what you will use
* `time` attribute on structural elements that indicates how long a test took to run \(in seconds\)

### Nice to have

* `<system-out>`, `<system-err>` that captures output from tests, preferably at the level of `<testcase>`
* `timestamp` attribute on structural elements that indicate when a test has run, preferrably on `<testcase>`

## Examples

Here's bare-bone example of a test report that works with Launchable:

```markup
<?xml version="1.0" encoding="UTF-8"?>
<testsuite time='0.050425' name="UserTest" timestamp="2020-11-18T19:22:24+09:00">
  <testcase time='0.025175' file="test/models/user_test.rb" name="test_should_save_user_with_name">
    <error/>
  </testcase>
  <testcase time='0.025250' file="test/models/user_test.rb" name="test_should_not_save_user_without_name">
  </testcase>
</testsuite>
```

Another one from Maven+Java+JUnit. This is not a file based test runner, so :

```markup
<?xml version="1.0" encoding="UTF-8"?>
<testsuite name="foo.FooTest" time="0">
  <testcase name="foo.FooTest.test3" classname="foo.FooTest" time="0.001">
    <failure type="java.lang.RuntimeException">java.lang.RuntimeException
    at foo.FooTest.test3(FooTest.java:7)
</failure>
  </testcase>
  <testcase name="foo.FooTest.test1" classname="foo.FooTest" time="0.001"/>
  <testcase name="foo.FooTest.test2" classname="foo.FooTest" time="0.003"/>
</testsuite>
```

