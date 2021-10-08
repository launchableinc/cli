---
description: >-
  Capturing test reports and selecting tests to run in multiple environments
  (e.g. browser tests, mobile tests, etc.)
---

# Use 'flavors' to run the best tests for an environment

Lots of teams run the same tests across several different environments. For example, a UI test suite might be run in several browsers in parallel. Or perhaps you need to build a slightly different version of a mobile app for different locales and need to run the same tests across all of them.

In these scenarios, a test result is not just a test result: it is the combination of the test _and_ the environment that it was run in. A test might pass in one environment but fail in another.

Launchable supports these scenarios with a new concept called **flavors**.

![](../.gitbook/assets/flavors-2x.png)

When you submit test results using `launchable record tests`, you can submit additional metadata in the form of key-value pairs using the `--flavor` option.

For example:

```bash
# run tests in Chrome and report results
cypress run --reporter junit --reporter-options "mochaFile=report/test-output-chrome.xml"

launchable record tests --build [BUILD NAME] --flavor browser=chrome cypress report/test-output-chrome.xml

# run tests in Firefox and report results
cypress run --reporter junit --reporter-options "mochaFile=report/test-output-firefox.xml"

launchable record tests --build [BUILD NAME] --flavor browser=firefox cypress report/test-output-firefox.xml
```

And so on. \(You can submit multiple key-value pairs, too: `--flavor key=value --flavor key2=value2`\)

Later, when you want to request a subset of tests, you can include the same key-value pairs to get a subset of tests specifically selected for that flavor.

For example:

```bash
# get a subset for Chrome, run it, then report results
find ./cypress/integration | launchable subset --build [BUILD NAME] --confidence 90% --flavor browser=chrome cypress > subset-chrome.txt

cypress run --spec "$(cat subset-chrome.txt)" --reporter junit --reporter-options "mochaFile=report/test-output-chrome.xml"

launchable record tests --build [BUILD NAME] --flavor browser=chrome cypress report/test-output-chrome.xml

# get a subset for Firefox, run it, then report results
find ./cypress/integration | launchable subset --build [BUILD NAME] --confidence 90% --flavor browser=firefox cypress > subset-firefox.txt

cypress run --spec "$(cat subset-firefox.txt)" --reporter junit --reporter-options "mochaFile=report/test-output-firefox.xml"

launchable record tests --build [BUILD NAME] --flavor browser=firefox cypress report/test-output-firefox.xml
```

This feature lets you select the right tests to run based on the changes being tested _and_ the environment they are being run in.

Note: if your workflow involves creating a session externally using `launchable record session`, you should set `--flavor` in _that_ command \(instead of `launchable subset` or `launchable record tests`, as they will be ignored\), such as:

```bash
launchable record session --build [BUILD NAME] --flavor browser=chrome > session.txt

find ./cypress/integration | launchable subset --session $(cat session.txt) --confidence 90% cypress > subset-chrome.txt

cypress run --spec "$(cat subset-chrome.txt)" --reporter junit --reporter-options "mochaFile=report/test-output-chrome.xml"

launchable record tests --session $(cat session.txt) cypress report/test-output-chrome.xml
```

