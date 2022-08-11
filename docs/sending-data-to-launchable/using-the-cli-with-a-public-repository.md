# Using the CLI with a public repository

{% hint style="info" %}
This page relates to [#creating-and-setting-your-api-key](../getting-started.md#creating-and-setting-your-api-key "mention").
{% endhint %}

Authentication between the Launchable CLI and Launchable API typically requires an API key. However, API keys cannot be used for open source projects in public repos since anyone can retrieve an API key by opening a pull request.

To solve this problem for open source projects, Launchable offers another authentication mechanism called **tokenless authentication**. Instead of using a static token, tokenless authentication uses a CI/CD service provider's public API to verify if tests are actually running in CI. With this feature, OSS contributors can analyze and optimize test execution without a static Launchable API token.

## Prerequisites

If your project is open source and you want to use Launchable,

* Your open source project needs to be hosted in a public GitHub repository
* Your open source project needs to use GitHub Actions for CI

## Preparation

1. [Sign up](http://app.launchableinc.com/signup) and create your [organization.md](../concepts/organization.md "mention") and [workspace.md](../concepts/workspace.md "mention")
2. [Contact us](https://www.launchableinc.com/support) to enable tokenless authentication for your project. We need to know your **Launchable organization**, **Launchable workspace**, and **GitHub repository URL**
3. Set some extra environment variables on GitHub Actions
4. Start using Launchable in your open source project

### Environment Variables

After we've enabled tokenless authentication for your project, you must set three environment variables in your CI pipeline:

* `LAUNCHABLE_ORGANIZATION`: Launchable organization name
* `LAUNCHABLE_WORKSPACE`: Launchable workspace name
* `GITHUB_PR_HEAD_SHA`: A pull request head SHA, which can be retrieved using `${{ github.event.pull_request.head.sha }}`

### Examples

Here's example of a GitHub Actions configuration with tokenless authentication:

```yaml
name: Verify Launchable tokenless authentication

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

    - name: Launchable
      run: |
        pip3 install --user launchable~=1.0
        export PATH=~/.local/bin:$PATH
        launchable verify
      working-directory: ./gradle
      env:
        GITHUB_PR_HEAD_SHA: ${{ github.event.pull_request.head.sha }}
```

To see how it works with an actual GitHub project, visit [launchableinc/examples](https://github.com/launchableinc/examples).
