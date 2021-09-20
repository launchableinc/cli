# Using the CLI with a public repository

## Background

Launchable uses an API token for authentication between Launchable CLI and Launchable API. However, an API token usually can not be used for Open Source project since anyone can send a Pull Request and retrieve the Token.

To solve the problem, Launchable prepares another authentication mechanism called tokenless authentication. Instead of a static token, tokenless authentication uses a CI/CD service provider's public API to verify if tests are actually running. With tokenless authentication, OSS contributes optimize test execution without a static Launchable API token.

## Prerequisites

* A project needs to be hosted on a public GitHub repository
* Currently, tokenless authentication supports GitHub Actions only

## Preparation

1. [Sign up](http://app.launchableinc.com/signup) and create an organization and a workspace 
2. [Contact us](https://www.launchableinc.com/support) and tell in which project you enable tokenless authentication
3. Set some extra environment variables on GitHub Actions

### Environment Variables

Three environment variables need to be set to enable tokenless authentication:

* `LAUNCHABLE_ORGANIZATION`: Launchable organization name
* `LAUNCHABLE_WORKSPACE`: Launchable workspace name
* `GITHUB_PR_HEAD_SHA`: A pull request head SHA, which can be retrieved from `${{ github.event.pull_request.head.sha }}`

### Examples

Here's example of a GitHub Actions configuration with tokenless authentication:

```yaml
name: Efficient pull request validation for Gradle example

on:
  pull_request:
    paths:
    - gradle/**

env:
  LAUNCHABLE_ORGANIZATION: "examples"
  LAUNCHABLE_WORKSPACE: "gradle"

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
      with:
        fetch-depth: 0
    - uses: actions/setup-python@v2
    - name: Set up JDK 1.8
      uses: actions/setup-java@v1
      with:
        java-version: 1.8

    - name: Pull request validation
      run: |
        # Get Launchable CLI installed. If you can, make it a part of the builder image to speed things up
        pip3 install --user launchable~=1.0 > /dev/null
        export PATH=~/.local/bin:$PATH

        set -x

        # Tell Launchable about the build you are producing and testing
        launchable record build --name $BUILD_NAME --source ..

        # Find 25% of the relevant tests to run for this change
        launchable subset --target 25% --build $GITHUB_RUN_ID gradle src/test/java > subset.txt

        function record() {
          # Record test results
          launchable record test --build $GITHUB_RUN_ID gradle build/test-results/test
        }

        trap record EXIT

        # Run gradle with the subset of tests
        ./gradlew test $(< subset.txt)
      working-directory: ./gradle
      env:
        GITHUB_PR_HEAD_SHA: ${{ github.event.pull_request.head.sha }}
```

For more examples and see how it works from an actual GitHub project, visit [launchableinc/examples](https://github.com/launchableinc/examples).

