# Using the CLI with a public repository

{% hint style="info" %}
This page relates to [#creating-and-setting-your-api-key](./#creating-and-setting-your-api-key "mention").
{% endhint %}

Authentication between the Launchable CLI and Launchable API typically requires an API key. However, API keys cannot be used for open source projects in public repositories since anyone can retrieve an API key by opening a pull request.

To solve this problem for open source projects, Launchable offers another authentication mechanism called **tokenless authentication**. Instead of using a static token, tokenless authentication uses a CI/CD service provider's public API to verify if tests are actually running in CI. With this feature, OSS contributors can analyze and optimize test execution without a static Launchable API token.

{% hint style="info" %}
These instructions changed in November 2022 with the introduction of OpenID Connect for authentication.

If you implemented tokenless authentication before November 2022, please follow [migration-to-github-oidc-auth.md](migration-to-github-oidc-auth.md "mention").
{% endhint %}

## Setting up tokenless authentication

### Prerequisites

If your project is open source and you want to use Launchable,

* Your open source project needs to be hosted in a public GitHub repository
* Your open source project needs to use GitHub Actions for CI

### Preparation

1. [Sign up](http://app.launchableinc.com/signup) and create your [organization.md](../../../concepts/organization.md "mention") and [workspace.md](../../../concepts/workspace.md "mention")
2. [Contact us](https://www.launchableinc.com/support) to enable tokenless authentication for your project. We need to know your **Launchable organization**, **Launchable workspace**, and **GitHub repository URL**
3. Update your GitHub Actions YAML
4. Start using Launchable in your open source project

#### GitHub Actions YAML configuration

After we've enabled tokenless authentication for your project, you must set three environment variables in your CI pipeline:

* `LAUNCHABLE_ORGANIZATION`: Launchable organization name
* `LAUNCHABLE_WORKSPACE`: Launchable workspace name
* `EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH`: Set this to `1`

Then, add/update the `permissions` section of your GitHub Actions YAML file.

Tokenless authentication relies on OpenID Connect (OIDC) tokens. In order to use OIDC token in GitHub Actions, you need to configure permissions to retrieve that. As described in the [GitHub Help Article](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings), `id-token: write` permission needs to be added.

This permission can be added per-job or to the entire workflow:

```yaml
name: Verify Launchable tokenless authentication

on:
  pull_request:
    paths:
      - gradle/**

env:
  LAUNCHABLE_ORGANIZATION: "examples"
  LAUNCHABLE_WORKSPACE: "gradle"
  EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH: 1

permissions:
  id-token: write
  contents: read

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
```

## About OpenID Connect (OIDC)

{% hint style="info" %}
In November 2022 we added support for OpenID Connect for authentication.

If you implemented tokenless authentication before November 2022, please follow [migration-to-github-oidc-auth.md](migration-to-github-oidc-auth.md "mention").
{% endhint %}

### OIDC implementation overview

GitHub now provides a short-lived signed token for each GitHub Actions run ([About security hardening with OpenID Connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)). This token is signed by GitHub's private key, and we can verify its validity via its public key. This makes the token a security credential that major Cloud providers such as AWS, Azure, and Google Cloud can use as an authentication token. Launchable implemented the same mechanism as these Cloud providers, so we can accept it as a credential.

### Frequently Asked Questions

**What is included in the OIDC token?**

GitHub provides a detailed explanation and example of the OIDC token. See [Understanding the OIDC token](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#understanding-the-oidc-token).

**How does Launchable verify the OIDC token?**

When you apply for tokenless authentication, we associate your GitHub repository with your Launchable workspace in our internal database.

When you run the CLI, the Launchable API server verifies the OIDC token and checks that the `repository` claim in it matches the stored association.

**Can I see how the CLI handles the OIDC token?**

Sure! Check out these commits in the public CLI repository:

1. [https://github.com/launchableinc/cli/commit/945597f3fffeb49cd5968ba29054de78505aab61](https://github.com/launchableinc/cli/commit/945597f3fffeb49cd5968ba29054de78505aab61)
2. [https://github.com/launchableinc/cli/commit/68b06c01607b43bed33b2f774f424f7a8c220af6](https://github.com/launchableinc/cli/commit/68b06c01607b43bed33b2f774f424f7a8c220af6)
