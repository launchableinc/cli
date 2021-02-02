# Bazel

## Recording test results

When you are running your tests with Bazel, simply point to the Bazel workspace to collect test results:

```bash
# run the tests however you normally do
bazel test //...

launchable record tests --build <BUILD NAME> bazel .
```
For more information and advanced options, run `launchable record tests bazel --help`


### Always run the command

`launchable record tests` requires always run whether test run succeeds or fails. The way depends on your CI environment. 

#### Jenkins
Jenkins has [`post { always { ... } }`](https://www.jenkins.io/doc/book/pipeline/syntax/#post) option:

```gradle
pipeline {
  ...
  bazel test //...
  ...
  post { 
    always {
      launchable record tests --build <BUILD NAME> bazel .
    }
  }
}
```

#### CircleCI
CircleCI has [`when: always`](https://circleci.com/docs/2.0/configuration-reference/#the-when-attribute) option:
```yaml
- jobs:
  - test:
    ...
    - run:
      name: Run tests
      command: bazel test //...
    - run:
      name: Record test results
      command: launchable record tests --build <BUILD NAME> bazel .
      when: always

```
#### Github Actions
GithubAction has [`if: ${{ always() }}`](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#always) option:

```yaml
jobs:
  test:
    steps:
      ...
      - name: Run tests
        run: bazel test //...
      - name: Record test result
        run: launchable record tests --build <BUILD NAME> bazel .
        if: always()
```

#### Bash
If you run tests on your local or other CI, you can use `trap`:
```bash
function record() {
  launchable record tests --build <BUILD NAME> bazel .
}
# set a trap to send test results to Launchable for this build either tests succeed/fail
trap record EXIT SIGHUP

bazel test //...
```

## Subsetting test execution

To select meaningful subset of tests, first list up all the test targets you consider running, for example:

```bash
# list up all test targets in the whole workspace
bazel query 'tests(//...)'

# list up all test targets referenced from the aggregated smoke tests target
bazel query 'test(//foo:smoke_tests)'
```

You feed that into `launchable subset bazel` to obtain the subset of those target:

```bash
bazel query 'tests(//...)' |
launchable subset \
    --build <BUILD NAME> \
    --target 10% \
    bazel > launchable-subset.txt
```

You can now invoke Bazel with it:

```bash
bazel test $(cat launchable-subset.txt)
```

