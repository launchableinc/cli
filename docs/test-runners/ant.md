# Ant

{% hint style="info" %}
Hey there, did you land here from search? FYI, Launchable helps teams test faster, push more commits, and ship more often without sacrificing quality \([here's how](https://www.launchableinc.com/how-it-works)\). [Sign up](https://app.launchableinc.com/signup) for a free trial for your team, then read on to see how to add Launchable to your testing pipeline.
{% endhint %}

## Getting started

First, follow the steps in the [Getting started](../getting-started.md) guide to install the Launchable CLI, set your API key, and verify your connection.

Then return to this page to complete the three steps of implementation:

1. Recording builds
2. Recording test results
3. Subsetting test execution

## Recording builds

Launchable selects tests based on the changes contained in a **build**. To send metadata about changes to Launchable, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`. See [Data privacy and protection](../security/data-privacy-and-protection.md) for more info.

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> ant <PATH TO JUNIT XML>
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../resources/always-run.md).
{% endhint %}

## Subsetting tests

Subsetting instructions differ depending on whether you plan to [shift tests left](../#shift-left) or [shift tests right](../#shift-right):

### Shift left

First, set up a new test execution job/step/pipeline to run earlier in your software development lifecyle.

Then, to retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
launchable subset 
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    ant <PATH TO SOURCE> > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.

This creates a file called `launchable-subset.txt` that you can embed into your `build.xml` to select files to run:

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

Finally, you run you test command like this:

```bash
ant junit
```

Make sure to continue running the full test suite at some stage. Run `launchable record build` and `launchable record tests` for those runs to continually train the model.

### Shift right

The [shift right](../#shift-right) diagram suggests first splitting your existing test run into two parts:

1. A subset of dynamically selected tests, and
2. The rest of the tests

To retrieve a subset of tests, first pass the full list of test candidates to `launchable subset`. For example:

```bash
launchable subset 
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    --rest launchable-remainder.txt \
    ant <PATH TO SOURCE> > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--target` option should be a percentage; we suggest `20%` to start. This creates a subset of the most important tests that will run in 20% of the full execution time. As the model learns from your builds, the tests in the subset will become more and more relevant.
* The `--rest` option writes all the other tests to a file so you can run them separately.

This creates two files called `launchable-subset.txt` and `launchable-remainder.txt` that you can embed into your `build.xml` to run tests in two stages:

```markup
<project>
  ...
  <target name="check-launchable">
    <available file="launchable-subset.txt" property="launchable"/>
  </target>
  <target name="check-launchable-reminder">
    <available file="launchable-remainder.txt" property="launchable-reminder"/>
  </target>

  <target name="junit" depends="jar,check-launchable,check-launchable-reminder">
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
          <includefile name="launchable-remainder.txt" if="${launchable-reminder}">
          <include name="**/*Test.java" unless="${launchable}" />
        </fileset>
      </batchtest>
    </junit>
  </target>
  ...
</project>
```

You can remove the `launchable-remainder.txt` related parts after we've let you know that the model is sufficiently trained. Once you do this, make sure to continue running the full test suite at some stage. Run `launchable record build` and `launchable record tests` for those runs to continually train the model.

