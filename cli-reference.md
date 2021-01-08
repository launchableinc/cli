# CLI reference

{% hint style="info" %}
Current as of:

* CLI version `1.0.2`
* Launchable version `e75d423`
{% endhint %}

## Getting started

### Requirements

* Python 3
* Java OR Docker

### Install

The Launchable CLI is a Python3 package that can be installed via pip:

```bash
$ pip3 install --user launchable~=1.0
```

This creates a `~/.local/bin/launchable` executable that should be in your `PATH`. \(See [PEP-370](https://www.python.org/dev/peps/pep-0370/) for further details.\)

### Authenticate

Set your API token:

```bash
$ export LAUNCHABLE_TOKEN=your_API_token
```

### Verify

Then run `launchable verify` in your environment to see if you've successfully configured the CLI. If it succeeds, you'll see a message like the one below. Otherwise, you'll see an error message.

```bash
$ launchable verify

Platform: macOS-10.15.7-x86_64-i386-64bit
Python version: 3.8.3
Java command: java
Your CLI configuration is successfully verified :tada:
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

```text
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

For more details about what we do with commits and what we don't, see [this block in the getting started guide](getting-started.md#recording-builds-and-commits).

### record session

Creates a record of a **test session** in Launchable.

```text
$ launchable record session [OPTIONS]
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--build BUILD_NAME` | Name of the build being tested. \(See `record build --name`\) | Yes |

This command tells Launchable that you are about to begin testing a build that was been recorded earlier with the `record build` command.

The command prints out a session ID to stdout which should be captured into an environment variable or a file.

### subset

Produces a subset of **tests** to pass to your test runner.

```text
launchable subset [OPTIONS] TESTRUNNER ...
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--session SESSIONID` | ID of the test session \(see `record session`\) | Yes |
| `--base DIR` | Advanced option. A large number of test runners use file names to identify tests, and for those test runners, so does Launchable. By default Launchable record test file names as given to it; IOW we expect those to be relative paths, so that identities of tests remain stable no matter where in the file system a Git workspace gets checked out. But in the rare circumstances where this behavior is inadequate, the `--base` option lets you specify a separate directory to relativize the path of tests before recording them. | No |
| `--target PERCENTAGE` | Create a time-based subset of the given percentage. \(`0%-100%`\) | Yes |

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`s, see [Integrations](integrations/).

### record tests

Send **test results** for the **test session** to Launchable.

```text
launchable record tests [OPTIONS] TESTRUNNER ...
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--session SESSIONID` | ID of the test session \(see `record session`\) | Yes |
| `--base DIR` | See the discussion of `launchable subset --base` option. | No |

This command reads JUnit XML report files produced by test runners and sends them to Launchable.

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`, see [Integrations](integrations/)

### verify

Verify that the CLI can communicate with the Launchable service and that you're authenticated properly.

```text
launchable verify
```

In order to avoid disrupting your CI/test process, the Launchable CLI is designed to tolerate & recover from service disruptions and other recoverable error conditions by falling back to no-op. This is an intentional design, but the downside is that such transparent failures can make troubleshooting difficult.

Therefore, we recommend you keep `launchable verify || true` in a recognizable spot in your CI process. This way, when you suspect a problem in Launchable, you can check the output of this command as a starting point.

