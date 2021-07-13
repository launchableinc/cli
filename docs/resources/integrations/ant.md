---
description: This page outlines how the Launchable CLI interfaces with Ant.
---

# Ant

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> ant <PATH TO JUNIT XML>
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

The high level flow for subsetting is:

1. Get the full list of tests/test paths and pass that to `launchable subset` with an optimization target for the subset
2. `launchable subset` will get a subset from the Launchable platform and output that list to a text file
3. Pass the text file into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
launchable subset 
    --build <BUILD NAME> \
    --target <PERCENTAGE DURATION> \
    ant <PATH TO SOURCE> > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/subsetting-your-test-runs.md) for more info.

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

