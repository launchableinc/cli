# CLI reference

## Getting started

### Requirements

* Python 3
* Java

### Install

The Launchable CLI is a Python3 package that can be installed via pip:

```bash
$ pip3 install --user --upgrade launchable~=1.0
```

This creates a `~/.local/bin/launchable` executable that should be in your `PATH`. \(See [PEP-370](https://www.python.org/dev/peps/pep-0370/) for further details.\)

### Authenticate

Set your API token:

```bash
$ export LAUNCHABLE_TOKEN=your_API_token
```

### Verify

Then run `launchable verify` in your CI environment to see if you've successfully configured the CLI. If it succeeds, you'll see a message like the one below. Otherwise, you'll see an error message.

```bash
$ launchable verify

Platform: macOS-11.1-x86_64-i386-64bit
Python version: 3.9.1
Java command: java
launchable version: 1.3.1
Your CLI configuration is successfully verified 🎉
```

## Commands

### record commit

Sends **commit** details to Launchable.

```bash
$ launchable record commit --source .
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--executable jar` | Run commit collection using Java. | No \(default\) |
| `--executable docker` | Run commit collection using Docker. | No |
| `--source DIR` | Path to a local Git repository/workspace. | No. Defaults to `$PWD` |

Commit collection happens automatically as a part of `record build`, so normally this command need not be invoked separately.

`--executable jar` is faster as the Java version of the commit collector is bundled with the CLI, but it requires that your system has Java installed. `--executable docker` allows you to run the equivalent commit collector packaged as a Docker image. You may choose to do this if your system allows you to run Docker containers but not Java. Containers will be downloaded on demand. This option is more of an escape hatch.

### record build

Creates a record of a **build** in Launchable.

```bash
$ launchable record build [OPTIONS]
```

<table>
  <thead>
    <tr>
      <th style="text-align:left">Option</th>
      <th style="text-align:left">Description</th>
      <th style="text-align:left">Required</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td style="text-align:left"><code>--name BUILD_NAME</code>
      </td>
      <td style="text-align:left">Unique identifier that you assign to your build. See <a href="https://github.com/launchableinc/mothership/tree/e92c456234009b918e9da4cce5ea9c425e337dc5/docs/getting-started/README.md#naming-builds">Naming builds</a> for
        more discussion of how to choose a build name.</td>
      <td style="text-align:left">Yes</td>
    </tr>
    <tr>
      <td style="text-align:left"><code>--source path/to/ws</code> or <code>--source main=path/to/ws</code>
      </td>
      <td style="text-align:left">
        <p>Path to a local Git repository/workspace. Use this option multiple times
          when code from multiple Git repositories are contributing to the build.
          Note that Git submodules are discovered and recorded automatically, so
          there&apos;s no need to enumerate them separately.</p>
        <p>To distinguish different Git repositories, every repository is labeled
          internally in Launchable. By default, the literal path given to this option
          is used as a label (for example, <code>label</code> would be <code>foo/bar</code> for <code>--source foo/bar</code>).
          If you wish to name labels explicitly (e.g. to keep them stable even when
          directory names move around), then you can specify a label by prepending
          a label name followed by <code>=</code>, such as <code>--source vendor=$VENDOR_PATH</code>.</p>
      </td>
      <td style="text-align:left">Yes</td>
    </tr>
  </tbody>
</table>

The act of recording a build teaches Launchable that the specified set of commits have turned into a build, and that this build is henceforth identified by the given name. This forms the basis of how Launchable calculates the changes.

For more details about what we do with commits and what we don't, see [this block in the getting started guide](../getting-started.md#recording-builds-and-commits).

### record session

Creates a record of a **test session** in Launchable.

```bash
$ launchable record session [OPTIONS]
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--build BUILD_NAME` | Name of the build being tested. \(See `record build --name`\) | Yes |
| `--no-save-file` | Instead of save a session ID to `~/.config/launchable/session.json`, output it to STDOUT | No |

This command tells Launchable that you are about to begin testing a build that was been recorded earlier with the `record build` command. This is only needed in more complex scenarios.

The command writes out a session ID to `~/.config/launchable/session.json`. Subsequent commands read the session ID from this file.

### subset

Produces a subset of **tests** to pass to your test runner.

```bash
launchable subset [OPTIONS] TESTRUNNER ...
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--build BUILD_NAME` | Name of the build being tested. \(See `record build --name`\) | One of `--build` or `--session` is required |
| `--session SESSIONID` | ID of the test session \(see `record session`\) | One of `--build` or `--session` is required |
| `--base DIR` | Advanced option. A large number of test runners use file names to identify tests, and for those test runners, so does Launchable. By default Launchable record test file names as given to it; IOW we expect those to be relative paths, so that identities of tests remain stable no matter where in the file system a Git workspace gets checked out. But in the rare circumstances where this behavior is inadequate, the `--base` option lets you specify a separate directory to relativize the path of tests before recording them. | No |
| `--target PERCENTAGE` | Create a time-based subset of the given percentage. \(`0%-100%`\) | Yes |

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`s, see [Integrations](cli-reference.md).

### record tests

Send **test results** for the **test session** to Launchable.

```bash
launchable record tests [OPTIONS] TESTRUNNER ...
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--build BUILD_NAME` | Name of the build being tested. \(See `record build --name`\) | One of `--build` or `--session` is required |
| `--session SESSIONID` | ID of the test session \(see `record session`\) | One of `--build` or `--session` is required |
| `--base DIR` | See the discussion of `launchable subset --base` option. | No |

This command reads JUnit XML report files produced by test runners and sends them to Launchable.

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`, see [Integrations](cli-reference.md)

### verify

Verify that the CLI can communicate with the Launchable service and that you're authenticated properly.

```bash
launchable verify
```

In order to avoid disrupting your CI/test process, the Launchable CLI is designed to tolerate & recover from service disruptions and other recoverable error conditions by falling back to no-op. This is an intentional design, but the downside is that such transparent failures can make troubleshooting difficult.

Therefore, we recommend you keep `launchable verify || true` in a recognizable spot in your CI process. This way, when you suspect a problem in Launchable, you can check the output of this command as a starting point.

{% hint style="info" %}
This documentation is current as of CLI version `1.3.1`
{% endhint %}

