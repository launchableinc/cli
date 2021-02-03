# CTest

## Recording test results

CTest does not natively produce JUnit compatible test report files, so you should use an extra tool such as [`xsltproc`](http://xmlsoft.org/xslt/xsltproc.html) and [`ctest-to-junit`](https://github.com/rpavlik/jenkins-ctest-plugin/blob/master/ctest-to-junit.xsl) to convert them for use with Launchable.

After running tests, point to the directory that contains all the generated test report XML files:

```bash
# run the tests however you normally do
# `-T test` option output own format XML file
ctest -T test --no-compress-output

# convert CTest's XML format to JUnit format with XSLT converter
xsltproc ctest-to-junit.xsl Testing/**/Test.xml > Testing/**/junit.xml

# record JUnit formatted XML
launchable record tests --build <BUILD NAME> ctest Testing/**/junit.xml
```

Note: `launchable record tests` requires always run whether test run succeeds or fails. See [Always record tests](always-run.md).

For more information and advanced options, run `launchable record tests ctest --help`

## Subsetting test execution

To select meaningful subset of tests, have GoogleTest list your test cases \([documentation](https://cmake.org/cmake/help/latest/manual/ctest.1.html)\), then feed that into Launchable CLI:

```bash
ctest -N | launchable subset ... ctest > launchable-subset.txt
```

The file will contain the subset of tests that should be run. Now invoke CTest by passing those as an argument:

```bash
# run the test
ctest -T test --no-compress-output -R $(cat launchable-subset.txt)
```

