# Go Test

```bash
go test -list ./... | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  go-test > launchable-subset.txt
```

```bash
go test -run $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report > report.xml
```

```bash
go test -list ./... | launchable subset \
  --build <BUILD NAME> \
  --target <TARGET> \
  --rest launchable-remainder.txt \
  go-test > launchable-subset.txt
```

```bash
go test -run $(cat launchable-subset.txt) ./... -v 2>&1 | go-junit-report > report.xml

go test -run $(cat launchable-remainder.txt) ./... -v 2>&1 | go-junit-report > report.xml
```

```bash
# install JUnit report formatter
go get -u github.com/jstemmer/go-junit-report

# run the tests however you normally do, then produce a JUnit XML file
go test -v ./... | go-junit-report > report.xml

launchable record tests --build <BUILD NAME> go-test .
```
