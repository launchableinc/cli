# Ensuring \`record tests\` always runs

The `launchable record tests` command must always run even if the test run succeeds or fails. However, some tools exit the build process as soon as the test process finishes, preventing this from happening. The way to fix this depends on your CI tool:

## Jenkins

Jenkins has [`post { always { ... } }`](https://www.jenkins.io/doc/book/pipeline/syntax/#post) option:

```text
pipeline {
  ...
  sh 'bundle exec rails test -v $(cat launchable-subset.txt)'
  ...
  post {
    always {
      sh 'launchable record tests <BUILD NAME> [OPTIONS]'
    }
  }
}
```

## CircleCI

CircleCI has [`when: always`](https://circleci.com/docs/2.0/configuration-reference/#the-when-attribute) option:

```yaml
- jobs:
  - test:
    ...
    - run:
        name: Run tests
        command: bundle exec rails test -v $(cat launchable-subset.txt)
    - run:
        name: Record test results
        command: launchable record tests <BUILD NAME> [OPTIONS]
        when: always
```

## Github Actions

GithubAction has [`if: ${{ always() }}`](https://docs.github.com/en/actions/reference/context-and-expression-syntax-for-github-actions#always) option:

```yaml
jobs:
  test:
    steps:
      ...
      - name: Run tests
        run: bundle exec rails test -v $(cat launchable-subset.txt)
      - name: Record test result
        run: launchable record tests <BUILD NAME> [OPTIONS]
        if: always()
```

## Bash

If you run tests on your local or other CI, you can use `trap`:

```bash
function record() {
  launchable record tests <BUILD NAME> [OPTIONS]
}
# set a trap to send test results to Launchable for this build either tests succeed/fail
trap record EXIT SIGHUP

bundle exec rails test -v $(cat launchable-subset.txt)
```

