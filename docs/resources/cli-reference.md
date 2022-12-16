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

| Option                         | Description                                                  | Required               |
| ------------------------------ | ------------------------------------------------------------ | ---------------------- |
| `--import-git-log-output FILE` | Path to a file that contains git-log output. See below.      | No.                    |
| `--max-days DAYS`              | The maximum number of days to collect commits retroactively. | No. Defaults to `30`   |
| `--source DIR`                 | Path to a local Git repository.                              | No. Defaults to `$PWD` |

Commit collection happens automatically as a part of `record build`, so normally this command need not be invoked separately. It's only used for [#multiple-repositories-built-deployed-separately-then-tested-together-e.g.-microservices](../sending-data-to-launchable/using-the-launchable-cli/recording-builds-with-the-launchable-cli/recording-builds-from-multiple-repositories.md#multiple-repositories-built-deployed-separately-then-tested-together-e.g.-microservices "mention").

#### \`--import-git-log-output\` option

Related to [running-under-restricted-networks.md](../sending-data-to-launchable/using-the-launchable-cli/recording-builds-with-the-launchable-cli/running-under-restricted-networks.md "mention").

If the `--import-git-log-output` option is used, instead of reading the commits from the repository specified by `--source`, it reads the specified file for the commit data. The input file should contain the output of this Git command:

```
git log --pretty='format:{"commit": "%H", "parents": "%P", "authorEmail": "%ae", "authorTime": "%aI", "committerEmail": "%ce", "committerTime": "%cI"}' --numstat
```

### record build

Creates a record of a [build.md](../concepts/build.md "mention") in Launchable.

```bash
launchable record build [OPTIONS]
```

| Option                                                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Required                                               |
| -------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| `--commit REPO_NAME=COMMIT_HASH`                         | For use with `--no-commit-collection` and `launchable record commit`.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               | No. When `--commit` is used, `--source` is unnecessary |
| `--max-days DAYS`                                        | The maximum number of days to collect commits retroactively.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | No. Defaults to `30`                                   |
| `--name BUILD_NAME`                                      | Unique identifier that you assign to your build. See [Naming builds](../sending-data-to-launchable/using-the-launchable-cli/recording-builds-with-the-launchable-cli/choosing-a-value-for-build-name.md) for more discussion of how to choose a build name.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | Yes                                                    |
| `--no-commit-collection`                                 | Disables commit collection when recording a build. You must run `launchable record commit` elsewhere in your pipeline if you use this option.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       | No                                                     |
| `--no-submodules`                                        | Stop collecting build information from Git Submodules.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No. Defaults to `False`                                |
| `--scrub-pii`                                            | No-op. Previously disabled collection of user full names and enabled user email address hashing. Now on by default.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | No. No-op                                              |
| `--source REPO_NAME=DIR` (recommended) or `--source DIR` | <p>Path to a local Git repository/workspace. Use this option multiple times when code from multiple Git repositories are contributing to the build. Note that Git submodules are discovered and recorded automatically, so there's no need to enumerate them separately.</p><p>To distinguish different Git repositories, every repository is labeled internally in Launchable. By default, the literal path given to this option is used as a label (for example, <code>label</code> would be <code>dir/source</code> for <code>--source dir/source</code>). We recommend naming labels explicitly (e.g. to keep them stable even when directory names move around), by prepending a label name followed by <code>=</code>, such as <code>--source vendor=$VENDOR_PATH</code>.</p> | No. Defaults to `$PWD`                                 |

The act of recording a build teaches Launchable that the specified set of commits have turned into a build, and that this build is henceforth identified by the given name. This forms the basis of how Launchable calculates the changes.

For more details about what we do with commits and what we don't, see [this block in the getting started guide](../sending-data-to-launchable/using-the-launchable-cli/getting-started/#recording-builds-and-commits).

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

### record tests

Send **test results** for the **test session** to Launchable.

```bash
launchable record tests [OPTIONS] TESTRUNNER ...
```

| Option                      | Description                                                                                                                                                                                                                                            | Required                                    |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------- |
| `--build BUILD_NAME`        | Name of the build being tested. (See `record build --name`)                                                                                                                                                                                            | One of `--build` or `--session` is required |
| `--session SESSIONID`       | ID of the test session (see `record session`)                                                                                                                                                                                                          | One of `--build` or `--session` is required |
| `--flavor KEY=VALUE`        | Advanced option. Submit additional non-code-related metadata that influenced the test results, such as environment. To be used in combination with `launchable subset --flavor`. Supports multiples, e.g. `--flavor key1=value1 --flavor key2=value2`. | No                                          |
| `--base DIR`                | See the explanation of `launchable subset --base` option above.                                                                                                                                                                                        | No                                          |
| `--group=GROUPNAME`         | Assigns all tests passed into this invocation to this group.                                                                                                                                                                                           | No                                          |
| `--allow-test-before-build` | Allow recording any test reports, even if they were created before the build was recorded.                                                                                                                                                             | No                                          |

This command reads JUnit (or similar) XML report files produced by test runners and sends them to Launchable.

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`, see [Integrations](cli-reference.md)

### split-subset

Splits an existing **subset** from Launchable into chunk(s). Related to [replacing-static-parallel-suites-with-a-dynamic-parallel-subset.md](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/replacing-static-parallel-suites-with-a-dynamic-parallel-subset.md "mention") and[using-groups-to-split-subsets.md](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/zero-input-subsetting/using-groups-to-split-subsets.md "mention").

<pre class="language-bash"><code class="lang-bash"><strong>launchable split-subset [OPTIONS] TESTRUNNER ...
</strong></code></pre>

Intended for use with `launchable subset` with the `--split` option.

#### Options for [replacing-static-parallel-suites-with-a-dynamic-parallel-subset.md](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/replacing-static-parallel-suites-with-a-dynamic-parallel-subset.md "mention")

| Option                         | Description                                                                                                                                                         | Required |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| `--bin BIN_NUMBER/BIN_COUNT`   | The portion of the subset to retrieve, e.g `--bin 1/3`                                                                                                              | Yes      |
| `--rest FILE`                  | Output the remainder of the subset to a file. This is useful for running the "rest of the tests" after you've run a subset.                                         | No       |
| `--same-bin FILE`              | \[Beta; [gradle.md](integrations/gradle.md "mention") only] Place tests listed in the FILE to belong to same bin in order to avoid the tests to run simultaneously. | No       |
| `--subset-id SUBSET-ID-STRING` | ID of the subset output from `launchable subset --split ...` (see `--split` under `subset`)                                                                         | Yes      |

#### Options for [using-groups-to-split-subsets.md](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/zero-input-subsetting/using-groups-to-split-subsets.md "mention")

| Option                       | Description                                                                                 | Required |
| ---------------------------- | ------------------------------------------------------------------------------------------- | -------- |
| `--split-by-group`           | Splits an existing subset output into multiple files. See below.                            | No       |
| `--split-by-group-with-rest` | Similar to `--split-by-group`, except remainder/rest files are also included. See below.    | No       |
| `--subset-id SUBSETID`       | ID of the subset output from `launchable subset --split ...` (see `--split` under `subset`) | Yes      |

**`--split-by-group` outputs**

When you run `launchable split-subset` with the `--split-by-group` option, the CLI creates several files:

* `subset-groups.txt`
  * By default, this file contains a list of the groups that you need to set up.
  * If `--output-exclusion-rules` was used with `launchable subset`, this file contains a list of the groups that you can skip entirely.
* `subset-[groupname].txt` (one file for each group)
  * Each file contains the normal subset output, but only for that group's tests. You can pass these files into the test process for each group.
  * By default, these files contain inclusion rules. If `--output-exclusion-rules` was used with `launchable subset`, these files will contain exclusion rules. You're supposed to **exclude** these tests.
* `subset-nogroup.txt`
  * This file contains tests that had no group assignment, if there are any.

**`--split-by-group-with-rest` outputs**

When you run `launchable split-subset` with the `--split-by-group-with-rest` option, the CLI creates several files:

* All of the files listed above under **`--split-by-group` outputs**
* `rest-groups.txt`
  * By default, this file contains a list of the groups that you don't need to set up.
  * If `--output-exclusion-rules` was used with `launchable subset`, this file contains a list of the groups that you can't skip.
* `rest-[groupname].txt` (one file for each group)
  * Each file contains the normal `--rest` (see [#subset](cli-reference.md#subset "mention")) output, but only for that group's tests.
  * By default, these files contain inclusion rules. If `--output-exclusion-rules` was used with `launchable subset`, these files will contain exclusion rules.&#x20;
* `rest-nogroup.txt`
  * This file contains `--rest` tests that had no group assignment, if there are any.

### stats test-sessions
Retrieves statistics about test sessions

```bash
launchable stat test-sessions
```

Output example:
```
{"averageDurationSeconds":653.168192926045,"count":311,"days":7}
```

| Option | Description | Required |
|----|----|----|
| `--days N` | Specifies the length of the time period to compute stats from. Longer time span produces more accurate and stable stats, but they react slowly to recent trend change. Note that the human working schedule tends to produce a weekly cycle, so multiples of 7 tend to produce a better result | No |
| `--flavor KEY=VALUE` | Limit the aggregation to test sessions with the specified flavor. If multiple `--flavor` options are specified, a test session mustthat have all the specified flavors to be factored in. | No |

Output is in JSON format:

| Field | Description                                                                                                                                |
|-------|--------------------------------------------------------------------------------------------------------------------------------------------|
| averageDurationSeconds | Average duration of this test session in seconds. A duration of a test session is a sum of all the durations of test cases that run in it. |
| count | Number of test sessions that occurred during this period.                                                                                  |
| days | The length of the time period from which the stats were calculated from, measured in days.                                                 |


### subset

Produces a subset of **tests** to pass to your test runner.

```bash
launchable subset [OPTIONS] TESTRUNNER ...
```

| Option                               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | Required                                                  |
| ------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| `--build BUILD_NAME`                 | Name of the build being tested. (See `record build --name`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | One of `--build` or `--session` is required               |
| `--session SESSION-ID-STRING`        | String output of  `launchable record session`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | One of `--build` or `--session` is required               |
| `--base DIR`                         | Advanced option. A large number of test runners use file names to identify tests, and for those test runners, so does Launchable. By default Launchable record test file names as given to it; in other words, we expect those to be relative paths, so that identities of tests remain stable no matter where in the file system a Git workspace gets checked out. But in the rare circumstances where this behavior is inadequate, the `--base` option lets you specify a separate directory to relativize the path of tests before recording them. | No                                                        |
| `--target PERCENTAGE`                | Create a variable time-based subset of the given percentage. (`0%-100%`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | No                                                        |
| `--time TIME`                        | Create a fixed time-based subset. Select the best set of tests that run within the given time bound. (e.g. `10m` for 10 minutes, `2h30m` for 2.5 hours, `1w3d` for 7+3=10 days. )                                                                                                                                                                                                                                                                                                                                                                     | No                                                        |
| `--confidence PERCENTAGE`            | Create a confidence-based subset of the given percentage. (`0%-100%`)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 | No                                                        |
| `--flavor KEY=VALUE`                 | Advanced option. Restrict the subset of tests by `flavor`. Flavors must be submitted ahead of time with test reports (see `launchable record tests --flavor` below). Supports multiples, e.g. `--flavor key1=value1 --flavor key2=value2`.                                                                                                                                                                                                                                                                                                            | No                                                        |
| `--rest FILE`                        | Output the remainder of the subset to a file. This is useful for running the "rest of the tests" after you've run a subset.                                                                                                                                                                                                                                                                                                                                                                                                                           | No                                                        |
| `--split`                            | Output a subset ID instead of the subset list itself. For use with `launchable split-subset`                                                                                                                                                                                                                                                                                                                                                                                                                                                          | No                                                        |
| `--ignore-new-tests`                 | Ignore tests that were not recognized by the subset service and are therefore assumed to be new tests. This option is useful if you want to prevent new tests (with unknown execution time) from increasing subset execution time, but it also means that it might take longer for new tests to be recognized (since they were not run in the subset). To maintain consistency between inputs to and outputs from `launchable subset`, these tests will be added to the end of the `--rest` file output (if that option is used)                      | No                                                        |
| `--get-tests-from-previous-sessions` | Let the server generate the full list of tests from which to create a subset of tests. Intended for use with `--output-exclusion-rules`, otherwise new tests might be skipped accidentally. See [zero-input-subsetting](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/zero-input-subsetting/ "mention")                                                                                                                                                                           | No                                                        |
| `--output-exclusion-rules`           | Output a list of tests to _exclude_ instead of a list of tests to _include_. See [zero-input-subsetting](../features/predictive-test-selection/requesting-and-running-a-subset-of-tests/subsetting-with-the-launchable-cli/zero-input-subsetting/ "mention")                                                                                                                                                                                                                                                                                          | No                                                        |
| `--ignore-flaky-tests-above`         | Ignore tests that flaky score is higher than the value as you set this option. You can confirm the flaky scores on WebApp.                      | No                                                        |

Exactly how this command generates the subset and what's required to do this depends on test runners. For available supported `TESTRUNNER`s, see [Integrations](integrations/).

When none of `--target`, `--time`, and `--confidence` is specified, Launchable
chooses the subset target. This is convenient on the initial setup when you are
not sure what the subset size should be. Later, you can choose the right target
after you see the statistics of your test suite and potential time-savings based
on the Launchable accumulated data.

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
