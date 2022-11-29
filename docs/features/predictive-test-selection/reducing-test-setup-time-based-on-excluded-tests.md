# Reducing the test setup time based on the excluded tests

Tests are not the only factor that slow down the CI process. The test setup
process such as building binaries, installing applications, or running servers
also contributes to the entire CI runtime. As Launchable excludes less likely
failing tests, some of those setups might become unnecessary depending on the
chosen tests. You can reduce the unnecessary setups by grouping the tests based
on the required setups.

## Example: Chrome and Firefox tests

Let's assume that you have tests that require Chrome and Firefox installed.
Before running tests, you need to install those browsers. Your CI script looks
like this:

```base
git checkout $COMMIT_HASH

./setup_chrome.sh
./run_chrome_tests.sh

./setup_firefox.sh
./run_firefox_tests.sh
```

Launchable's Predictive Test Selection will choose which tests to run among all
Chrome and Firefox tests. Depending on the situation, it might exclude all
Chrome tests and only run some Firefox tests. In this example, we will setup the
CI pipelines to reduce the unnecessary setup time as well as the less risky
tests.

We will have two CI pipeline setups. One is a post-merge full run test pipeline:

```base
# Post-merge full run setup
git checkout $COMMIT_HASH

launchable record session --build $BUILD_NAME > session.txt

./setup_chrome.sh
./run_chrome_tests.sh
launchable record tests --session $(cat session.txt) --group=chrome file ./test-report/chrome/*.xml

./setup_firefox.sh
./run_firefox_tests.sh
launchable record tests --session $(cat session.txt) --group=firefox file ./test-report/firefox/*.xml
```

In the post-merge pipeline, we run all tests and upload the test results to
Launchable along with the test group names (e.g. `--group=chrome`). This enables
Launchable to learn which test belongs to which group.

As the second CI pipeline, we will have a pre-merge test pipeline with
Predictive Test Selection:

```base
# Pre-merge Predictive Test Selection run setup
git checkout $COMMIT_HASH

launchable record session --build $BUILD_NAME > session.txt
launchable subset --session $(cat session.txt) \
    --split \
    --target 50% \
    --get-tests-from-previous-sessions \
    --output-exclusion-rules > subset-id.txt

# This command writes "subset-groups.txt", "subset-chrome.txt", and
# "subset-firefox.txt".
launchable split-subset --subset-id $(cat subset-id.txt) --split-by-groups

# If chrome group has a test, run the chosen tests.
if grep chrome subset-groups.txt; then
  ./setup_chrome.sh
  ./run_chrome_tests.sh $(cat subset-chrome.txt)
  launchable record tests --session $(cat session.txt) --group=chrome file ./test-report/chrome/*.xml
fi

# If firefox group has a test, run the chosen tests.
if grep firefox subset-groups.txt; then
  ./setup_firefox.sh
  ./run_firefox_tests.sh $(cat subset-firefox.txt)
  launchable record tests --session $(cat session.txt) --group=firefox file ./test-report/firefox/*.xml
fi
```

Launchable learns the list of all tests from the post-merge full run pipeline.
In the pre-merge pipeline, we instruct Launchable to choose which tests to
exclude based on that list (`--get-tests-from-previous-sessions`). After that
choice is made, split the tests based on the test groups. In this example,
`chrome` and `firefox` groups are specified in the full run pipeline.
`launchable split-subset` command writes several files based on the groups it
learnt:

* `subset-groups.txt`: This file has group names that have at least one test
  chosen to run.
* `subset-$GROUP_NAME.txt`: This file is created for each group that has a test
  chosen to run.

In this example, if Predictive Test Selection chooses to run some Firefox tests
and excludes all Chrome tests, `subset-groups.txt` will contain `firefox` only
and there will be `subset-firefox.txt` file that specifies chosen Firefox tests
to run. With the CI script above, Chrome tests will be skipped along with its
setup process because `subset-groups.txt` doesn't have `chrome` group name in
it.
