# Migrating to the GitHub OIDC Authentication

{% hint style="info" %}
This page relates to [#creating-and-setting-your-api-key](../getting-started.md#creating-and-setting-your-api-key "mention") and
[Using the CLI with a public repository](./using-the-cli-with-a-public-repository.md "mention").
{% endhint %}

For public repositories, Launchable has been offering GitHub Actions specialized
authentication method. We are now migrating this method to the new OpenID
Connect (OIDC) based one. This new method provides more secure and scalable way
to authenticate to Launchable.

## Overview of the Migration

GitHub started providing a short-lived signed token for each GitHub Actions run
([About security hardening with OpenID
Connect](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)).
This token is signed by GitHub's private key, and we can verify its validity via
its public key. This makes the token a security credential, and major Cloud
providers such as AWS, Azure, and Google Cloud can take it as an authentication
token. Launchable implemented the same mechanism as these Cloud providers and
now we can take it as a credential.

The new method provides the same benefit as the previous GitHub tokenless auth
Launchable provided; no API key is needed. On top of that, the new method
provides more security as it's using a verifiable short-lived token. The new
method also helps Launchable to scale and be stable. Because the previous method
requires Launchable to call GitHub APIs, the authentication process occasionally
hits its API limit, which ends up in request failures. With the new method, we
no longer need a GitHub API call, and this makes the service stable.

## Migration Process

The new OIDC based authentication is supported from CLI v1.52.0. If you install
the latest CLI, you should get the necessary version automatically.

### Environment Variables

You must set three environment variables:

- `LAUNCHABLE_ORGANIZATION`: Launchable organization name
- `LAUNCHABLE_WORKSPACE`: Launchable workspace name
- `EXPERIMENTAL_GITHUB_OIDC_TOKEN_AUTH`: Set this to 1 to enable the new auth.

`GITHUB_PR_HEAD_SHA` is no longer needed.

### GitHub Actions Permissions

In order to use OIDC token in GitHub Actions, you need to configure permissions
to retrieve that. As described in the [GitHub Help
Article](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#adding-permissions-settings),
`id-token: write` permission needs to be added.

This permission can be added per-step or to the entire workflow.

### Examples

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
        permissions:
          id-token: write
        run: |
          pip3 install --user launchable~=1.0
          export PATH=~/.local/bin:$PATH
          launchable verify
        working-directory: ./gradle
```

## Questions and Answers

- What is included in the OIDC token?

  GitHub provides a detailed explanation and example of the OIDC token
  ([Understanding the OIDC
  token](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect#understanding-the-oidc-token)).

- How does Launchable verify the OIDC token?

  When you sign up for the GitHub tokenless auth, we associate your GitHub
  repository with your Launchable workspace in our internal database. Launchable
  API server verifies the OIDC tokens and checks that the `repository` claim in
  it matches with the association.

- Can I see how the CLI handles the OIDC token?

  See
  https://github.com/launchableinc/cli/commit/945597f3fffeb49cd5968ba29054de78505aab61
  and https://github.com/launchableinc/cli/commit/68b06c01607b43bed33b2f774f424f7a8c220af6
