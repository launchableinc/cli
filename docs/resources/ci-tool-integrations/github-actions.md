---
description: This page outlines Launchable's custom GitHub actions.
---

# GitHub Actions

## [Launchable record build and test results action](https://github.com/marketplace/actions/record-build-and-test-results-action)

Launchable record build and test results action enables you to integrate Launchable into your CI in simple way with less change. This action installs the [CLI](https://github.com/launchableinc/cli) and runs `launchable record build` and `launchable record test` to send data to Launchable so that the test results will be analyzed in [Launchable](https://www.launchableinc.com/) to improve your developer productivity. You still need to add [subset request command](https://docs.launchableinc.com/resources/cli-reference#subset) to retrieve test subset.

### Example usage

```yaml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  LAUNCHABLE_TOKEN: ${{ secrets.LAUNCHABLE_TOKEN }}
  LAUNCHABLE_DEBUG: 1
  LAUNCHABLE_REPORT_ERROR: 1

jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Test
        run: <YOUR TEST COMMAND HERE>
      - name: Record
        uses: launchableinc/record-build-and-test-results-action@v1.0.0
        with:
          source: .
          build_name: $GITHUB_RUN_ID
          test_runner: <YOUR TEST RUNNER HERE>
          report: .
        if: always()
```
