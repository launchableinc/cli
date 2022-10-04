# Running under restricted networks

{% hint style="info" %}
This page relates to [#recording-builds](./#recording-builds "mention").
{% endhint %}

Launchable CLI requires the Internet connection, but your environment might have
a limited Internet reachability. This page explains how to deal with it in
common cases.

## Outbound traffic control

Networks can have a network policy that limits the connections to certain IP
addresses and ports. In this case, you need to allowlist Launchable's API server
IP addresses. We have an API endpoint that has a stable IP address.

* Domain: `api-static.mercury.launchableinc.com`
* IP Addresses: `13.248.185.38` and `76.223.54.162`
* Port: `443` (HTTPS)

Once your network is configured to allow traffic to the IP addresses above, you
can configure the Launchable CLI to use that endpoint:

```bash
export LAUNCHABLE_BASE_URL="https://api-static.mercury.launchableinc.com"
launchable verify
```

## Git repository in an Internet unreachable environment

Your repository might have no Internet access for security reasons. For example,
the CI workflow would look like:

1. Check out the Git repository in a machine with no Internet connection.
2. Build the artifacts in the machine.
3. Transfer the artifacts to a test environment that has the Internet
   connection.
4. Run tests against the artifacts in the test environment.

In this case, you can save the `git log` output to a file and transfer that file
to the test environment so that Launchable CLI can see the changes under test.

In the build machine, you will need to run a `git log` command with
`--pretty='format:{"commit": "%H", "parents": "%P", "authorEmail": "%ae",
"authorTime": "%aI", "committerEmail": "%ce", "committerTime": "%cI"}'
--numstat`. You need to limit the number of commits to be written out. You can
use `--max-count` option. Typically 10 to 20 commits should be suffice. Advanced
users can tweak the ranges as needed to limit the amount of data.

```bash
# Check out the repository and build artifacts
git clone https://git.internal.example.com/repo
cd repo
make all

# Save git log data to a file. Using --max-count to limit the number of commits.
git log --pretty='format:{"commit": "%H", "parents": "%P", "authorEmail": "%ae", "authorTime": "%aI", "committerEmail": "%ce", "committerTime": "%cI"}' --numstat  --max-count 10 > git_log_output
# Save the current commit hash
git rev-parse HEAD > git_commit_hash

# Save the artifacts and git outputs
scp server_test_bin git_log_output git_commit_hash fileserver.internal.example.com:
```

The git log output (`git_log_output` file above) should contain the content like
below:

```
{"commit": "1f0c18ea3df6575b4132b311d52a339af34c90ba", "parents": "b068a8a515e6cbbb2d6673ddb2c421939bd618b7", "authorEmail": "example1@example.com", "authorTime": "2022-09-21T15:59:21-07:00", "committerEmail": "example1@example.com", "committerTime": "2022-09-21T16:34:35-07:00"}
24	4	main.cc
24	0	main_test.cc

{"commit": "b068a8a515e6cbbb2d6673ddb2c421939bd618b7", "parents": "cb1d1b797726fe16e661d8377bd807f2508e9df4", "authorEmail": "example2@example.com", "authorTime": "2022-09-16T17:03:52+00:00", "committerEmail": "example3@example.com", "committerTime": "2022-09-16T17:03:52+00:00"}
1	1	docs/README.md
```

In the test machine, you will need to use these files to upload the commit data.

```bash
scp -R fileserver.internal.example.com: .

# Record commits and build
BUILD_NAME=build-$(cat git_commit_hash)
launchable record commit --import-git-log-output git_log_output
launchable record build --no-commit-collection --commit .=$(cat git_commit_hash) --name $BUILD_NAME
launchable record session --name $BUILD_NAME

# Run tests
./server_test_bin
```
