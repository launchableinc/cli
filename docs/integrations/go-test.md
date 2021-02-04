# Go Test

## Recording test results

Go Test does not natively produce JUnit compatible test report files, so you should use an extra tool such as [github.com/jstemmer/go-junit-report](https://github.com/jstemmer/go-junit-report) to convert them for use with Launchable.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# install JUnit report formatter
go get -u github.com/jstemmer/go-junit-report

# run the tests however you normally do, then produce a JUnit XML file
go test -v ./... | go-junit-report > report.xml

launchable record tests ... go-test .
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](../resources/always-run.md).

For more information and advanced options, run `launchable record tests go-test --help`

## Subsetting test execution

To select a meaningful subset of tests, have Go Test list your test cases \([upstream documentation](https://golang.org/cmd/go/#hdr-Testing_flags)\), then feed that into Launchable CLI:

```bash
go test -list ./... | launchable subset ... go-test > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
go test -run $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report > report.xml
```

