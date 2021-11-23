---
description: This page outlines how the Launchable CLI interfaces with CTest.
---

# CTest

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started/), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

Run the tests with `ctest -T test --no-compress-output`. These options make sure the test results are written under the `Testing` directory.

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
launchable record tests --build <BUILD NAME> ctest Testing/**/Test.xml
```

{% hint style="warning" %}
You might need to take extra steps to make sure that `launchable record tests` always runs even if the build fails. See [Always record tests](../../sending-data-to-launchable/ensuring-record-tests-always-runs.md).
{% endhint %}

## Subsetting your test runs

The high level flow for subsetting is:

1.  Get the full list of tests/test paths and pass that to `launchable subset`

    with an optimization target for the subset
2.  `launchable subset` will get a subset from the Launchable platform and output

    that list to text files
3. Pass the text files into your test runner to run only those tests

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
# --show-only=json-v1 option outputs test list as JSON
ctest --show-only=json-v1 > test_list.json
launchable subset \
    --build <BUILD NAME> \
    --confidence <TARGET> \
    --output-regex-files \
    --output-regex-files-dir=subsets \
    ctest test_list.json
```

*   The `--build` should use the same `<BUILD NAME>` value that you used before in

    `launchable record build`.
*   The `--confidence` option should be a percentage; we suggest `90%` to start.

    You can also use `--time` or `--target`; see \[Subsetting your test

    runs]\(../../actions/subsetting-your-test-runs.md) for more info.
*   The `--output-regex-files` instructs CLI to write the regular expression for

    the subset tests into the directory specified in `--output-regex-files-dir`.

This creates files under the `subsets` directory. There are two sets of files. `subset_N` are the files that contain regular expressions of the chosen subset of tests. `rest_N` are the files for non-chosen tests.

```bash
# run the tests
for file in subset/subset_*; do
  ctest -T test --no-compress-output -R "$(cat "$file")"
done
```

### Obsolete usage

{% hint style="warning" %}
CTest has a size limit on the regular expression used for specifying which tests to run (`-R` argument in `ctest`). This causes an issue when running subsets. To address this issue, the CLI learned to split the regular expression into multiple files. The following usage is now obsolete. Please migrate to the new usage described above.
{% endhint %}

To retrieve a subset of tests, first list all the tests you would normally run and pass that to `launchable subset`:

```bash
# --show-only=json-v1 option outputs test list as JSON
ctest --show-only=json-v1 > test_list.json
launchable subset \
    --build <BUILD NAME> \
    --confidence <TARGET> \
    ctest test_list.json > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../actions/predictive-test-selection/subsetting-your-test-runs.md) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
# run the tests
ctest -T test --no-compress-output -R $(cat launchable-subset.txt)
```
