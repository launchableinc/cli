# DIY generic integration

<a name="record-tests"></a>
## Recording test results

TBD TBD TBD

In this example, test reports are stored in the `/test/reports/` directory:

```bash
launchable record tests \
    --name $BUILD_NAME \
    --session "$LAUNCHABLE_SESSION" \
    generic ~/test/reports/*.xml
```

Test reports should use the JUnit XML format. Most build tools and test runners can output results in this format, although you may need to enable it.

That makes the complete implementation of the test step:

```bash
# create a session
export LAUNCHABLE_SESSION = $(launchable record session)

# run tests!
# [TODO]

# send test reports
launchable record tests \
    --name $BUILD_NAME \
    --session "$LAUNCHABLE_SESSION" \
    generic ~/test/reports/*.xml
```

<a name="subset"></a>
## Subset test execution

TBD TBD TBD

```bash
find test -regex .*_test.rb | 
launchable optimize tests \
    --name $BUILD_NAME \
    --session "$LAUNCHABLE_SESSION" \
    --target 0.10 \
    generic > launchable-subset.txt
```
