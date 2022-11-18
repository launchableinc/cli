# Product overview

[Launchable](https://www.launchableinc.com) is a **software development intelligence platform** currently focused on continuous integration (CI). Using data from your CI runs, Launchable provides various features to speed up your testing workflow so you can ship high quality software faster.

## Predictive Test Selection

[predictive-test-selection](features/predictive-test-selection/ "mention") uses machine learning to select the right tests to run for a specific code change. This unlocks the ability to run a much smaller set of tests at various points in your software development lifecycle, accelerating delivery.

With Predictive Test Selection, Launchable actually tells your test runner exactly which tests to run based on data from past test runs and the changes being tested:

![](<.gitbook/assets/subsetting diagram@2x.png>)

Check out the full [Predictive Test Selection](features/predictive-test-selection/) page for more info.

## Test Insights

Launchable also analyzes your test data in aggregate to surface [insights](features/insights/ "mention"). You can use this information to improve the health of your test suite and get maximum value out of your test runs.

### Trends

The [trends.md](features/insights/trends.md "mention") page shows aggregate info about your test sessions, including average test session duration, test session frequency, and how often sessions fail.

Seeing this data over time gives you a picture of how your test suite evolves; for example, perhaps your tests are taking twice as long as they did six months ago, and you need to cut it down! Similarly, perhaps your team's running tests a lot more often than expected, which is driving up resource costs. Or maybe you have some broken tests that are driving up the overall failure rate.

![](.gitbook/assets/Insights.png)

### Flaky tests

Launchable also surfaces [flaky-tests.md](features/insights/flaky-tests.md "mention") in your test suite so you can fix them and run tests more reliably. Each test gets a score based on past results; a higher score means the test exhibits more flakiness and should be fixed ASAP!

![](<.gitbook/assets/Flaky tests - complete.png>)

## Test results and reports

As soon as you start sending test results to Launchable using the Launchable CLI, you can view [test-results-and-reports.md](features/test-results-and-reports.md "mention") in the Launchable dashboard. Launchable provides a richer view into test results, helping developers triage failures and fix them more quickly.

![](<.gitbook/assets/Test session details - with content.png>)

For quick access to this page, the Launchable CLI prints out a link to the results view every time you record results:

![](<.gitbook/assets/Link to results.png>)

In addition, Launchable shows all of your test runs in one place for easy navigation. No more digging around build logs:

![](<.gitbook/assets/Test runs - with content.png>)

## Test notifications via Slack

{% hint style="info" %}
The Launchable Slack app is currently available in a closed beta program. To apply to join the program, [fill out this form](https://forms.gle/8eUtAba1yzmNAigZA)!
{% endhint %}

The **Launchable Slack app** provides [test-notifications-via-slack.md](features/test-notifications-via-slack.md "mention") so that developers can immediately take action on the results, whether that's triaging failures or merging a PR. Developers can create subscriptions to receive personal notifications about test sessions run against their branches/pull requests or other test sessions they care about.

![](<.gitbook/assets/Slack desktop with app messages.png>)

The app sends notifications _directly_ to developers so they don't have to manually check their email or navigate to their pull request to see if their tests passed.
