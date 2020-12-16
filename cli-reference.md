# CLI reference

{% hint style="info" %}
Current as of:

* CLI version `0.1.10`
* Launchable version `c8e1c42`
{% endhint %}

## Getting started

### Requirements

* Python 3
* Java OR the ability to run Docker

### Install

The Launchable CLI is a Python3 package that can be installed via pip.

```bash
$ pip3 install --user launchable
```

This creates a `~/.local/bin/launchable` executable that should be in your `PATH`. See [PEP-370](https://www.python.org/dev/peps/pep-0370/) for further details.

### Authenticate

Set your API token:

```bash
$ export LAUNCHABLE_TOKEN=your_API_token
```

### Verify

Then run `launchable verify` in your environment to see if you've successfully configured the CLI.  If it succeeds, you'll see a message like the one below. Otherwise, you'll see an error message.

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

```text
$ launchable record commit --source .
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--executable [jar|docker]`  | Run commit collection using Docker \(default\) or Java .jar | No |
| `--source TEXT` | Repository path | Yes |

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
      <td style="text-align:left"><code>--name BUILD_ID</code>
      </td>
      <td style="text-align:left">ID for the build</td>
      <td style="text-align:left">Yes</td>
    </tr>
    <tr>
      <td style="text-align:left"><code>--source REPO_NAME</code>
      </td>
      <td style="text-align:left">
        <p>Repository name(s) and district(s), e.g.</p>
        <p><code>--source .</code> or <code>--source main=./main --source lib=./lib</code>
        </p>
      </td>
      <td style="text-align:left">Yes</td>
    </tr>
    <tr>
      <td style="text-align:left"><code>--with-commit</code>
      </td>
      <td style="text-align:left">Run commit collection at the same time</td>
      <td style="text-align:left">No</td>
    </tr>
    <tr>
      <td style="text-align:left"><code>--without-commit</code>
      </td>
      <td style="text-align:left">Do not run commit collection at the same time</td>
      <td style="text-align:left">No</td>
    </tr>
  </tbody>
</table>

### record session

Creates a record of a **test session** in Launchable. 

```text
$ launchable record session [OPTIONS]
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--name BUILD_ID` | ID of the build being tested \(see `record build`\) | Yes |

### optimize test

Asks Launchable for a list of optimized **tests**.

```text
launchable optimize test [OPTIONS] TEST_PATHS...
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--name BUILD_ID` | ID of the build being tested \(see `record build`\) | Yes |
| `--session INTEGER` | ID of the test session \(see `record session`\) | Yes |
| `--source REPO_NAME` |  | No |
| `--target FLOAT` | Subsetting target percentage \(`0.0 - 1.0`\) | Yes |

### record test

Send **test results** for the **test session** to Launchable.

```text
launchable record test [OPTIONS] XML_PATHS...
```

| Option | Description | Required |
| :--- | :--- | :--- |
| `--name BUILD_ID` | ID of the build being tested \(see `record build`\) | Yes |
| `--session INTEGER` | ID of the test session \(see `record session`\) | Yes |
| `--source REPO_NAME` |  | No |
| `--target FLOAT` | Subsetting target percentage \(`0.0 - 1.0`\) | Yes |

### verify

Verify that the CLI can communicate with the Launchable service and that you're authenticated properly.

```text
launchable verify
```

