# Updating tokenless authentication to use GitHub OIDC

{% hint style="info" %}
This page relates to [#creating-and-setting-your-api-key](./#creating-and-setting-your-api-key "mention") and [using-the-cli-with-a-public-repository.md](using-the-cli-with-a-public-repository.md "mention").
{% endhint %}

**Tokenless authentication** is Launchable's specialized authentication method for public repositories that use GitHub Actions for CI.

To make this method more scalable and secure, we are updating it to use OpenID Connect (OIDC). **This change requires action on your part.**

## OIDC implementation overview

GitHub now provides a short-lived signed token for each GitHub Actions run ([About security hardening with OpenID Connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)). This token is signed by GitHub's private key, and we can verify its validity via its public key. This makes the token a security credential that major Cloud providers such as AWS, Azure, and Google Cloud can use as an authentication token. Launchable implemented the same mechanism as these Cloud providers, so now we can accept it as a credential.

The new implementation of tokenless authentication provides the same benefit as the previous one: no API key is needed.

However, on top of that, the new implementation provides more security as it uses a verifiable short-lived token. It also helps Launchable scale and remain stable. Because the previous implementation involved calling GitHub APIs, the authentication process occasionally hit its API limit, resulting in request failures. With the new implementation, we no longer need to hit the GitHub API, which this makes the service more stable.

## Migration process

### Steps

To migrate to the new implementation, follow these steps:

1. The new OIDC based authentication is supported from CLI v1.52.0. If you typically install the latest CLI using `pip3 install --upgrade`, you will get the necessary version automatically. Otherwise you need to upgrade to the latest version.
2. Add/update the `permissions` section of your GitHub Actions YAML file. (See [#github-actions-permissions](migration-to-github-oidc-auth.md#github-actions-permissions "mention") below).
3. Add a new `EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH` environment variable. Set this to `1` to enable the new auth implementation.
4. Remove the `GITHUB_PR_HEAD_SHA` environment variable. It is no longer needed.
5. Keep the `LAUNCHABLE_ORGANIZATION` and `LAUNCHABLE_WORKSPACE` environment variables that were already set.

### Environment variables summary

| API implementation (original)                           | OIDC implementation (new)                                                      |
| ------------------------------------------------------- | ------------------------------------------------------------------------------ |
| `LAUNCHABLE_ORGANIZATION`: Launchable organization name | `LAUNCHABLE_ORGANIZATION`: Launchable organization name                        |
| `LAUNCHABLE_WORKSPACE`: Launchable workspace name       | `LAUNCHABLE_WORKSPACE`: Launchable workspace name                              |
| `GITHUB_PR_HEAD_SHA`                                    | `EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH`: Set this to `1` to enable the new auth. |

### GitHub Actions Permissions

In order to use OIDC token in GitHub Actions, you need to configure permissions to retrieve that. As described in the [GitHub Help Article](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings), `id-token: write` permission needs to be added.

This permission can be added per-job or to the entire workflow.

#### Examples

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

## Frequently Asked Questions

**What is included in the OIDC token?**

GitHub provides a detailed explanation and example of the OIDC token. See [Understanding the OIDC token](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#understanding-the-oidc-token).

**How does Launchable verify the OIDC token?**

When you apply for tokenless authentication, we associate your GitHub repository with your Launchable workspace in our internal database.

When you run the CLI, the Launchable API server verifies the OIDC token and checks that the `repository` claim in it matches the stored association.

**Can I see how the CLI handles the OIDC token?**

Sure! Check out these commits in the public CLI repository:

1. [https://github.com/launchableinc/cli/commit/945597f3fffeb49cd5968ba29054de78505aab61](https://github.com/launchableinc/cli/commit/945597f3fffeb49cd5968ba29054de78505aab61)
2. [https://github.com/launchableinc/cli/commit/68b06c01607b43bed33b2f774f424f7a8c220af6](https://github.com/launchableinc/cli/commit/68b06c01607b43bed33b2f774f424f7a8c220af6)
