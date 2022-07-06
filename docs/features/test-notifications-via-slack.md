# Test notifications via Slack

{% hint style="info" %}
The Launchable Slack app is currently available in a closed beta program. To apply to join the program, [fill out this form](https://forms.gle/8eUtAba1yzmNAigZA)!
{% endhint %}

The **Launchable Slack app** notifies developers when their test sessions finish so they can immediately take action on the results, whether that's triaging failures or merging a PR. Developers can create subscriptions to receive personal notifications about test sessions run against their branches/pull requests or other test sessions they care about.

![](<../.gitbook/assets/Slack desktop with app messages.png>)

## Getting started

To set up notifications:

1. Start sending data to Launchable
2. Install the Launchable Slack app in your Slack workspace
3. Link your Launchable account and your Slack account
4. Create your first notification subscription in Slack

## Sending data to Launchable

See [sending-data-to-launchable](../sending-data-to-launchable/ "mention")

## Installing the Launchable Slack app

{% hint style="info" %}
The Launchable Slack app is currently available in a closed beta program. To apply to join the program, [fill out this form](https://forms.gle/8eUtAba1yzmNAigZA)!
{% endhint %}

1. Log into the [Launchable dashboard](https://app.launchableinc.com/).
2. Click the ⚙️ cog icon to go to Settings.
3. Click the **Install Slack App** button in the Slack app section. _Only for beta program participants._\
   This will open the Slack app authorization flow. You may need to log in to Slack at this stage.
4. Authorize the app to install it.
5. Done! 🎉

## Linking your Launchable and Slack accounts

Once the Launchable Slack app has been installed, you and your teammates can link your Launchable and Slack accounts. This lets you set up subscriptions via the app.

{% hint style="info" %}
If you haven't signed up for Launchable yet, or if you're not a member of your team's Launchable organization yet, ask a teammate to send you an [#organization-invitation-link](../concepts/organization.md#organization-invitation-link "mention") so you can sign up (if needed) and join.
{% endhint %}

You communicate with the app through direct messages:

1. In Slack, click the New message icon in the top section of the left navigation (or use the Command+N or Control+N keyboard shortcut) to compose a new message.
2. In the "To:" field, type **Launchable** and select the app from the dropdown list.
3. In the message text field, type **/launchable link \[organization-id]** and hit Enter. (You can find your organization ID in the URL of any Launchable page.)
4. Click the button in the response message to initiate the flow to connect your Launchable account to your Slack account.

## Creating a notification subscription

After you've linked your Launchable and Slack accounts, you can create your first notification subscription.

Just like when you linked your account, you'll create a subscription by sending a message to the Launchable app. The syntax for creating a subscription is:

```
/launchable subscribe <WORKSPACE> <KEY>=<VALUE>
```

* `<WORKSPACE>` is the name of the workspace containing the test sessions you want to be notified about.
* `<KEY>=<VALUE>` is a key-value pair that contains the CI environment variable and value that indicates test sessions you want to subscribe to (e.g. `GITHUB_ACTOR=octocat`). More on this below ⤵

### Common key-value pairs for subscriptions

Typically, you'll want to be notified about _your_ test runs. Each CI system has its own environment variable that indicates the user that kicked off a build or pipeline.

For example, GitHub Actions has an environment variable called `GITHUB_ACTOR`. So if you use GitHub Actions, you can subscribe to your test runs using a command such as:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> GITHUB_ACTOR=<YOUR_GITHUB_USERNAME>
```

The tabbed section below describes how to compose `/launchable subscribe` for major CI tools:

{% tabs %}
{% tab title="Azure DevOps" %}
| Environment variable | `Build.RequestedForEmail`                        |
| -------------------- | ------------------------------------------------ |
| Description          | The person who pushed or checked in the changes. |

Example:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> Build.RequestedForEmail=<YOUR_EMAIL_ADDRESS>
```
{% endtab %}

{% tab title="CircleCI" %}
| Environment variable | `CIRCLE_USERNAME`                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Description          | The GitHub or Bitbucket username of the user who triggered the pipeline (only if the user has a CircleCI account). |

Example:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> CIRCLE_USERNAME=<YOUR_GITHUB_OR_BITBUCKET_USERNAME>
```
{% endtab %}

{% tab title="GitHub Actions" %}
| Environment variable | `GITHUB_ACTOR`                                                                     |
| -------------------- | ---------------------------------------------------------------------------------- |
| Description          | The name of the person or app that initiated the workflow. For example, `octocat`. |

Example:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> GITHUB_ACTOR=<YOUR_GITHUB_USERNAME>
```
{% endtab %}

{% tab title="GitLab CI" %}
{% hint style="info" %}
GitLab CI has 2 environment variables you can use.
{% endhint %}

| Environment variable | `GITLAB_USER_EMAIL`                        |
| -------------------- | ------------------------------------------ |
| Description          | The email of the user who started the job. |

Example:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> GITLAB_USER_EMAIL=<YOUR_GITLAB_EMAIL_ADDRESS>
```



| Environment variable | `GITLAB_USER_LOGIN`                                 |
| -------------------- | --------------------------------------------------- |
| Description          | The login username of the user who started the job. |

Example:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> GITLAB_USER_LOGIN=<YOUR_GITLAB_USERNAME>
```




{% endtab %}

{% tab title="Jenkins" %}
{% hint style="info" %}
Requires the **build user vars** Jenkins plugin: [https://plugins.jenkins.io/build-user-vars-plugin/](https://plugins.jenkins.io/build-user-vars-plugin/)
{% endhint %}

| Environment variable | `BUILD_USER_EMAIL`                               |
| -------------------- | ------------------------------------------------ |
| Description          | Email address of the user who started the build. |

Example:

```
/launchable subscribe <YOUR_LAUNCHABLE_WORKSPACE> BUILD_USER_EMAIL=<YOUR_EMAIL_ADDRESS>
```
{% endtab %}
{% endtabs %}

### Other key-value pairs

Since the subscription mechanism is based on CI environment variables, you have a lot of flexibility when it comes to subscriptions. CI tools expose lots of environment variables (and you can add your own) that you can pass into `/launchable subscribe` to create your own custom subscriptions. For more info, check out your CI tool's documentation.

## Receiving notifications

Once you've set up a subscription, the Launchable app will send you a personal message each time a new test session matching the subscription criteria is recorded:

|                          Passing notification                         |                         Failing notification                         |
| :-------------------------------------------------------------------: | :------------------------------------------------------------------: |
| ![](<../.gitbook/assets/Exportable passing session notification.png>) | ![](<../.gitbook/assets/Exportable failed session notification.png>) |

Failing notifications include a link to view test results in Launchable along with a quick summary of failing tests. This helps you get started triaging without checking your email over and over!
