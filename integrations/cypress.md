# Cypress

## Recording test results

Cypress provides a JUnit report runner. See [Reporters | Cypress Documentation](https://docs.cypress.io/guides/tooling/reporters.html)

After running tests, point to files that contains all the generated test report XML files:

```bash
# run the tests however you normally do, then produce a JUnit XML file
cypress run --reporter junit --reporter-options "mochaFile=report/test-output-[hash].xml"

launchable record tests ... cypress ./report/*.xml
```

For more information and advanced options, run `launchable record tests cypress --help`

## Subsetting test execution

To select a meaningful subset of tests, then feed that into Launchable CLI:
`cypress/integrations` is a default directory that are located test files and you can [edit](https://docs.cypress.io/guides/core-concepts/writing-and-organizing-tests.html#Test-files).

```bash
find ./cypress/integrations | launchable subset ...  cypress > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
cypress run --spec "$(cat launchable-subset.txt)"
```
