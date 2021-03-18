# Go Test

## Recording builds

Launchable chooses which tests to run based on the changes contained in a **build**. To enable this, you need to send build information to Launchable.

Right before you run create a build in your CI script, invoke the Launchable CLI as follows:

```bash
launchable record build --name <BUILD NAME> --source <PATH TO SOURCE>
```

With the `--name` option, you assign a unique identifier to this build. You will use this value later when you request a subset and record test results. See [Choosing a value for `<BUILD NAME>`](../resources/build-names.md) for tips on choosing this value.

The `--source` option points to the local copy of the Git repository used to produce this build, such as `.` or `src`.

## Subsetting tests

To select a meaningful subset of tests, have Go Test list your test cases \([upstream documentation](https://golang.org/cmd/go/#hdr-Testing_flags)\), then feed that into Launchable CLI:

```bash
go test -list ./... | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  go-test > launchable-subset.txt
```

The file will contain the subset of tests that should be run. You can now invoke your test executable to run exactly those tests:

```bash
go test -run $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report > report.xml
```

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

{% hint style="warning" %}
To make sure that `launchable record tests` always runs even if the build fails, see [Always record tests](recording-test-results.md#always-record-tests).
{% endhint %}

For more information and advanced options, run `launchable record tests go-test --help`