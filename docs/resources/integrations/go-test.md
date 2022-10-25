---
description: This page outlines how the Launchable CLI interfaces with Go Test.
---

# Go Test

{% hint style="info" %}
This is a reference page. See [Getting started](../../getting-started.md), [Sending data to Launchable](../../sending-data-to-launchable/), and [Subsetting your test runs](../../features/predictive-test-selection/) for more comprehensive usage guidelines.
{% endhint %}

## Recording test results

After running tests, point the CLI to your test report files to collect test results and train the model:

```bash
# install JUnit report formatter
go get -u github.com/jstemmer/go-junit-report

# run the tests however you normally do, then produce a JUnit XML file
go test -v ./... | go-junit-report -set-exit-code > report.xml

launchable record tests --build <BUILD NAME> go-test .
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
go test -list="Test|Example" . ./... | launchable subset \
  --build <BUILD NAME> \
  --confidence <TARGET> \
  go-test > launchable-subset.txt
```

* The `--build` should use the same `<BUILD NAME>` value that you used before in `launchable record build`.
* The `--confidence` option should be a percentage; we suggest `90%` to start. You can also use `--time` or `--target`; see [Subsetting your test runs](../../features/predictive-test-selection/) for more info.

This creates a file called `launchable-subset.txt` that you can pass into your command to run tests:

```bash
go test -run $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report > report.xml
```

## Example integration to your CI/CD

### GitHub Actions
You can easily integrate to your GitHub Actions pipeline.

```yaml
name: go-test-example

on:
  push:
    branches: [main]

env:
  LAUNCHABLE_TOKEN: ${{ secrets.LAUNCHABLE_TOKEN }}
  LAUNCHABLE_DEBUG: 1
  LAUNCHABLE_REPORT_ERROR: 1

jobs:
  tests:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: go
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
      # You need JDK 1.8.
      - name: Set up JDK 1.8
        uses: actions/setup-java@v1
        with:
          java-version: 1.8
      - name: Set up Go
        uses: actions/setup-go@v2
        with:
          go-version: 1.19
      # Install go-junit-report.
      - name: Install dependencies
        run: |
          go install github.com/jstemmer/go-junit-report@latest
      - name: Run test
        run: |
          # Install launchable CLI.
          python -m pip install --upgrade pip
          pip install wheel setuptools_scm
          pip install launchable

          # Verify launchable command.
          launchable verify

          # Record build name.
          launchable record build --name ${{ github.sha }} --source src=.

          # Subset tests up to 80% of whole tests.
          go test -list . ./... | launchable subset --build ${{ github.sha }} --target 80% go-test > launchable-subset.txt

          # Run subset test and export the result to report.xml.
          go test $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report -set-exit-code > report.xml

          # Record test result.
          launchable record tests --build ${{ github.sha }} go-test report.xml
```
