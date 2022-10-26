# CLI reference

## Getting started

### Requirements

* Python 3.5 or newer
* Java 8 or newer

### Install

The Launchable CLI is a Python3 package that can be installed via pip:

```bash
pip3 install --user --upgrade launchable~=1.0
```

This creates a `~/.local/bin/launchable` executable that should be in your `PATH`. (See [PEP-370](https://www.python.org/dev/peps/pep-0370/) for further details.)

### Authenticate

Set your API key:

```bash
export LAUNCHABLE_TOKEN=your_API_key
```

### Verify

Then run `launchable verify` in your CI environment to see if you've successfully configured the CLI. If it succeeds, you'll see a message like the one below. If you see an error message, see [Troubleshooting](troubleshooting.md).

```bash
$ launchable verify

Organization: <organization>
Workspace: <workspace>
Proxy: None
Platform: 'macOS-12.0.1-x86_64-i386-64bit'
Python version: '3.9.9'
Java command: 'java'
launchable version: '1.34.0'
Your CLI configuration is successfully verified 🎉
```

## Commands

### inspect subset

Display the details of a **subset** request. See [Subsetting your test runs](../features/predictive-test-selection/#inspecting-subset-details) for more info.

```
launchable inspect subset --subset-id 26876
```

| Option           | Description                                                                           | Required |
| ---------------- | ------------------------------------------------------------------------------------- | -------- |
| `--subset-id ID` | The ID of the subset request. Can be obtained from the output of `launchable subset`. | Yes      |

You can use `launchable inspect subset` to inspect the details of a specific subset, including rank and expected duration. This is useful for verifying that you passed the correct tests or test directory path(s) into `launchable subset`.

The output from `launchable subset` includes a tip to run `launchable inspect subset`:

```bash
$ launchable subset --build 123 --confidence 90% minitest test/*.rb > subset.txt

< summary table >

Run `launchable inspect subset --subset-id 26876` to view full subset details
```

Running that command will output a table containing a row for each test including:

* Rank/order
* Test identifier
* Whether the test was included in the subset
* Launchable's estimated duration for the test
  * Tests with a duration of `.001` seconds were not recognized by Launchable

{% hint style="success" %}
Note that the hierarchy level of the items in the list depends on the test runner in use.

For example, since Maven can accept a list of test _classes_ as input, `launchable inspect subset` will output a prioritized list of test _classes_. Similarly, since Cypress can accept a list of test _files_ as input, `launchable inspect subset` will output a list of prioritized test _files_. (And so on.)
{% endhint %}

### inspect tests

Display the details of a **record tests** command. See [Sending data to Launchable](../sending-data-to-launchable/#inspecting-uploaded-test-results) for more info.

```
launchable inspect tests --test-session-id 209575
```

| Option                 | Description                                                                               | Required |
| ---------------------- | ----------------------------------------------------------------------------------------- | -------- |
| `--test-session-id ID` | The ID of the test session. Can be obtained from the output of `launchable record tests`. | Yes      |

### record commit

Sends **commit** details to Launchable.

```bash
launchable record commit --source ./src
```

| Option                          | Description                                                  | Required               |
| ------------------------------- | ------------------------------------------------------------ | ---------------------- |
| `--max-days DAYS`               | The maximum number of days to collect commits retroactively. | No. Defaults to `30`   |
| `--source DIR`                  | Path to a local Git repository.                              | No. Defaults to `$PWD` |
| `--import-git-log-output FILE`  | Path to a file that contains git-log output.                 | No.                    |

Commit collection happens automatically as a part of `record build`, so normally this command need not be invoked separately.

If `--import-git-log-output` option is used, instead of reading the commits from
the repository specified by `--source`, it reads the specified file for the
commit data. The file should contain the output of `git log` with options
`--pretty='format:{"commit": "%H", "parents": "%P", "authorEmail": "%ae",
"authorTime": "%aI", "committerEmail": "%ce", "committerTime": "%cI"}'
--numstat`.

### record build

Creates a record of a **build** in Launchable.

```bash
launchable record build [OPTIONS]
```

| Option                                                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Required                                               |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `--name BUILD_NAME`                                      | Unique identifier that you assign to your build. See [Naming builds](../sending-data-to-launchable/choosing-a-value-for-build-name.md) for more discussion of how to choose a build name.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Yes                                                    |
| `--max-days DAYS`                                        | The maximum number of days to collect commits retroactively.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | No. Defaults to `30`                                   |
| `--no-submodules`                                        | Stop collecting build information from Git Submodules.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No. Defaults to `False`                                |
| `--source REPO_NAME=DIR` (recommended) or `--source DIR` | <p>Path to a local Git repository/workspace. Use this option multiple times when code from multiple Git repositories are contributing to the build. Note that Git submodules are discovered and recorded automatically, so there's no need to enumerate them separately.</p><p>To distinguish different Git repositories, every repository is labeled internally in Launchable. By default, the literal path given to this option is used as a label (for example, <code>label</code> would be <code>dir/source</code> for <code>--source dir/source</code>). We recommend naming labels explicitly (e.g. to keep them stable even when directory names move around), by prepending a label name followed by <code>=</code>, such as <code>--source vendor=$VENDOR_PATH</code>.</p> | No. Defaults to `$PWD`                                 |
| `--scrub-pii`                                            | No-op. Previously disabled collection of user full names and enabled user email address hashing. Now on by default.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | No. No-op                                              |
| `--no-commit-collection`                                 | Disables commit collection when recording a build. You must run `launchable record commit` elsewhere in your pipeline if you use this option.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | No                                                     |
| `--commit REPO_NAME=COMMIT_HASH`                         | For use with `--no-commit-collection` and `launchable record commit`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | No. When `--commit` is used, `--source` is unnecessary |

The act of recording a build teaches Launchable that the specified set of commits have turned into a build, and that this build is henceforth identified by the given name. This forms the basis of how Launchable calculates the changes.

For more details about what we do with commits and what we don't, see [this block in the getting started guide](../getting-started.md#recording-builds-and-commits).

### record session

Creates a record of a **test session** in Launchable.

```bash
launchable record session [OPTIONS]
```

| Option               | Description                                                 | Required |
| -------------------- | ----------------------------------------------------------- | -------- |
| `--build BUILD_NAME` | Name of the build being tested. (See `record build --name`) | Yes      |

This command tells Launchable that you are about to begin testing a build that was been recorded earlier with the `record build` command. This is only needed in more complex scenarios.

The command outputs a string that you can save for use in other commands (like `launchable subset` and `launchable record tests`) in lieu of `--build`. We suggest saving the value either to an environment variable or to a text file:

```bash
# environment variable

launchable record build --name BUILD_NAME [OPTIONS]
export LAUNCHABLE_SESSION=$(launchable record session --build BUILD_NAME)
<run tests>
launchable record tests --session $LAUNCHABLE_SESSION [OPTIONS]
```

```bash
# text file

launchable record build --name BUILD_NAME [OPTIONS]
launchable record session --build BUILD_NAME > launchable-session.txt
<run tests>
launchable record tests --session $(cat launchable-session.txt) [OPTIONS]
```

(Otherwise, the command will write out a session ID to `~/.config/launchable/sessions/{hash}.txt`. This location may change in the future, so don't rely on it.)

### split-subset

Retrieves a specific portion of an existing **subset** from Launchable. See [replacing static parallel suites with a dynamic parallel subset](../features/predictive-test-selection/#replacing-static-parallel-suites-with-a-dynamic-parallel-subset).

```bash
launchable split-subset [OPTIONS] TESTRUNNER ...
```

| Option                       | Description                                                                                                                     | Required |
|------------------------------|---------------------------------------------------------------------------------------------------------------------------------| -------- |
| `--subset-id SUBSETID`       | ID of the subset output from `launchable subset --split ...` (see `--split` under `subset`)                                     | Yes      |
| `--bin BIN_NUMBER/BIN_COUNT` | The portion of the subset to retrieve                                                                                           | Yes      |
| `--rest FILE`                | Output the remainder of the subset to a file. This is useful for running the "rest of the tests" after you've run a subset.     | No       |
| `--same-bin FILE`            | [Beta; Gradle only] Place tests listed in the FILE to belong to same bin in order to avoid the tests to run simultaneously. | No       |

### subset

Produces a subset of **tests** to pass to your test runner.

```bash
launchable subset [OPTIONS] TESTRUNNER ...
```

| Option                               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | Required                                                  |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `--build BUILD_NAME`                 | Name of the build being tested. (See `record build --name`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | One of `--build` or `--session` is required               |
| `--session SESSIONID`                | ID of the test session (see `record session`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | One of `--build` or `--session` is required               |
| `--base DIR`                         | Advanced option. A large number of test runners use file names to identify tests, and for those test runners, so does Launchable. By default Launchable record test file names as given to it; IOW we expect those to be relative paths, so that identities of tests remain stable no matter where in the file system a Git workspace gets checked out. But in the rare circumstances where this behavior is inadequate, the `--base` option lets you specify a separate directory to relativize the path of tests before recording them. | No                                                        |
| `--target PERCENTAGE`                | Create a variable time-based subset of the given percentage. (`0%-100%`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                  | One of `--target`, `--time` or `--confidence` is required |
| `--time TIME`                        | Create a fixed time-based subset. Select the best set of tests that run within the given time bound. (e.g. `10m` for 10 minutes, `2h30m` for 2.5 hours, `1w3d` for 7+3=10 days. )                                                                                                                                                                                                                                                                                                                                                         | One of `--target`, `--time` or `--confidence` is required |
| `--confidence PERCENTAGE`            | Create a confidence-based subset of the given percentage. (`0%-100%`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                     | One of `--target`, `--time` or `--confidence` is required |
| `--flavor KEY=VALUE`                 | Advanced option. Restrict the subset of tests by `flavor`. Flavors must be submitted ahead of time with test reports (see `launchable record tests --flavor` below). Supports multiples, e.g. `--flavor key1=value1 --flavor key2=value2`.                                                                                                                                                                                                                                                                                                | No                                                        |
| `--rest FILE`                        | Output the remainder of the subset to a file. This is useful for running the "rest of the tests" after you've run a subset.                                                                                                                    | No                                                        |
| `--split`                            | Output a subset ID instead of the subset list itself. For use with `launchable split-subset`                                                                                                                                                                                                                                                                                                                                                                                                                                              | No                                                        |
| `--ignore-new-tests`                 | Ignore tests that were not recognized by the subset service and are therefore assumed to be new tests. This option is useful if you want to prevent new tests (with unknown execution time) from increasing subset execution time, but it also means that it might take longer for new tests to be recognized (since they were not run in the subset). To maintain consistency between inputs to and outputs from `launchable subset`, these tests will be added to the end of the `--rest` file output (if that option is used)          | No                                                        |
| `--get-tests-from-previous-sessions` | Let the server generate the full list of tests from which to create a subset of tests. Intended for use with `--output-exclusion-rules`, otherwise new tests might be skipped accidentally. See [zero-input-subsetting.md](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting.md "mention")                                                                                                                                                                                             | No                                                        |
| `--output-exclusion-rules`           | Output a list of tests to _exclude_ instead of a list of tests to _include_. See [zero-input-subsetting.md](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/zero-input-subsetting.md "mention")                                                                                                                                                                                                                                                                                                            | No                                                        |

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`s, see [Integrations](integrations/).

### record tests

Send **test results** for the **test session** to Launchable.

```bash
launchable record tests [OPTIONS] TESTRUNNER ...
```

| Option                | Description                                                                                                                                                                                                                                            | Required                                    |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| `--build BUILD_NAME`  | Name of the build being tested. (See `record build --name`)                                                                                                                                                                                            | One of `--build` or `--session` is required |
| `--session SESSIONID` | ID of the test session (see `record session`)                                                                                                                                                                                                          | One of `--build` or `--session` is required |
| `--flavor KEY=VALUE`  | Advanced option. Submit additional non-code-related metadata that influenced the test results, such as environment. To be used in combination with `launchable subset --flavor`. Supports multiples, e.g. `--flavor key1=value1 --flavor key2=value2`. | No                                          |
| `--base DIR`          | See the explanation of `launchable subset --base` option above.                                                                                                                                                                                        | No                                          |

This command reads JUnit (or similar) XML report files produced by test runners and sends them to Launchable.

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`, see [Integrations](cli-reference.md)

### verify

Verify that the CLI can communicate with the Launchable service and that you're authenticated properly.

```bash
launchable verify
```

In order to avoid disrupting your CI/test process, the Launchable CLI is designed to tolerate & recover from service disruptions and other recoverable error conditions by falling back to no-op. This is an intentional design, but the downside is that such transparent failures can make troubleshooting difficult.

Therefore, we recommend you keep `launchable verify || true` in a recognizable spot in your CI process. This way, when you suspect a problem in Launchable, you can check the output of this command as a starting point.

## Global options

### --dry-run

The dry-run mode does not actually send a payload to the server, and it is helpful to check the behavior. You can also see which APIs will be requested and their payload contents in the output.

The payload contents will be output as an audit log, so if the log level is higher than the audit level, it will be forced to be set to the audit level.

Strictly speaking, it does not mean that no requests will be sent at all, but GET requests with no payload data or side effects may be sent. This is because sometimes the response data from the GET request is needed to assemble subsequent requests.

### --log-level

You can use the `--log-level` option to output extra information from each command.

`--log-level audit` is particularly useful if you want to see exactly what data gets passed to Launchable when you run CLI commands. For example:

```
% launchable --log-level audit record build --name 1234 --source src=.
Processed 1 commits
AUDIT:launchable:send request method:post path:/intake/organizations/launchableinc/workspaces/awilkes/builds headers:{'Content-Type': 'application/json'} args:{'data': b'{"buildNumber": "1234", "commitHashes": [{"repositoryName": "src", "commitHash": "45b2e6d9df8e0013334354f30df1978c8b4196f8"}]}', 'timeout': (5, 60)}
```

### --plugins

You can use the `--plugins` option to tell the CLI where to look for custom profiles/plugins.

For example, if you have developed (or been provided) a custom profile file named `myProfile.py`, place that file in the directory of your choosing (e.g. `~/launchable-plugins`) and use it like this:

```bash
launchable --plugins ~/launchable-plugins record tests --build $BUILD myProfile /path/to/reports
```

Since `--plugins` is a global option, make sure to place it right after `launchable` but before `subset` or `record` in your command.
