# Workspace

A **workspace** contains all your **test sessions** and **builds** for a specific test suite. Each workspace belongs to an **organization**.

Launchable takes the data you send to your workspace and uses it to provide added value such as insights and predictive test selection.

## Test suites and workspaces

As mentioned above, a workspace should house data for a specific test suite. This means that your team might need multiple workspaces in your organization.

However "test suite" is a fairly ambiguous term that means different things to different teams, so let's expand on this.

{% hint style="info" %}
If you need to create another workspace in your organization, contact your customer success manager or email [support@launchableinc.com](mailto:support@launchableinc.com).
{% endhint %}

{% hint style="success" %}
You can switch between workspaces in your organization using the dropdown menu in the left navigation.
{% endhint %}

### Suites divided by test types and/or test runners

Many teams already divide their tests into logical groups based on:

1. the **type** of test (e.g. unit tests vs. UI tests, etc.),
2. the **tech stack** used to run those tests (e.g. Maven for unit tests vs. Cypress for UI tests, etc.), or
3. both (in most cases)

If your team thinks about test suites in this way, then the decision should be straightforward: for example, you should send all your Maven unit tests into one workspace and all your Cypress UI tests into another.

### Suites divided by test characteristics

If your team does _not_ think about test suites in this way - for example, perhaps you use a custom test runner that abstracts away some of the tech stack differences - then you should divide your tests into different workspaces based on their **characteristics**. All of the test info you send to a specific workspace should exhibit similar characteristics, such as:

1. **Test count and test duration** - For example, unit test suites tend to have lots of very short tests; in contrast, UI test suites tend to have fewer tests that take longer to run
2. **Overall duration** - some test suites take minutes whereas others can take hours of machine time to run
3. **Frequency** - Many teams run different suites in different phases of their software delivery lifecycle, usually based on how long they take to run
4. **Failures** - Some test suites fail more often than others, and within those failures, sometimes lots of tests fail versus only a few. Similarly, some suites are more **flaky** than others

Common characteristics between tests in a workspace are important for two reasons:

1. Test insights are aggregated at the workspace level. If you mix tests with different characteristics, insights such as flakiness scoring will be less useful
2. Predictive Test Selection models are evaluated at the workspace level. If you mix tests with lots of different characteristics, it will be harder to choose the correct optimization target

### Sub-suites within larger test suites

Sometimes teams consider small groups of tests _within_ larger suites as suites also.

For example, a team might have a large group of tests that they refer to as a "Regression test suite." Then, within that larger group, they divide tests into sub-suites based on components, like "Authentication," "API," etc. You might call these "sub-suites."

Sometimes the entire test suite runs (perhaps nightly), and other times perhaps only sub-suites are run.

If this applies to your team, we recommend using a single workspace for the entire _larger_ suite. In the example above, that team would have one workspace for the "Regression test suite."

{% hint style="info" %}
If you need to create another workspace in your organization, contact your customer success manager or email [support@launchableinc.com](mailto:support@launchableinc.com).
{% endhint %}

## Workspace settings

Workspace settings can be found on the settings page in any workspace:

![](../.gitbook/assets/launchable\_settings\_20220613.png)

### Workspace API key

Each workspace gets it own API key for CLI authentication. See [Getting started](../getting-started.md#setting-your-api-key) for more info on how to use API keys.

![](../.gitbook/assets/launchable\_API\_key\_setting\_20210613.png)

For security reasons, API keys can't be recovered once they've been created. If you lose your workspace API key, you'll need to create a new one and update your CI scripts.
