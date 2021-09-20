---
description: Your data is our highest priority
---

# Data privacy and protection

## Purpose and use of collected information

Launchable’s predictive test selection service learns the relationship between code changes and the test cases impacted by those changes.

### Does Launchable use the personal information for any purpose outside providing the services?

No.

### Does Launchable use any anonymized or aggregate data for any independent purpose outside of providing the services?

No.

## Specifics on the data sent to Launchable

### Does Launchable need access to my source code?

The actual content of your source code is not needed, only metadata about changes.

### What data is sent to Launchable?

The two key inputs for this are:

* Metadata \('features'\) about the **code changes being tested**, which includes:
  * the names and paths of files added/removed/modified in the change
  * number of modified lines in files in the change
  * Git commit hashes associated with the change
  * Git author details associated with those commits
* Metadata \('features'\) about the **test cases that were run**, which includes:
  * the names and paths of test cases and test files
  * pass/fail/skipped status of each test case
  * the duration of each test case
  * test case associations to test suites \(e.g. ‘unit tests,' ‘integration tests,’ etc.\)

See [Data examples](data-examples.md) for example `POST` bodies of what precisely is sent. You can also use the `--log-level audit` global option when you invoke the CLI to view exactly what data was passed in the request. See [CLI reference](../../resources/cli-reference.md#log-level).

## Data storage and retention

### Does Launchable encrypt personal information?

We encrypt data in transit and at rest.

### How does Launchable store customer data?

Launchable is a multi-tenant SaaS product. Each customer’s data is kept separate from each other.

### Where is the customer data stored specifically?

Launchable is hosted on AWS' US-West region.

### How long is customer data retained by Launchable? Will customer data be deleted or returned at the end of the engagement?

The customer has an option to have their data deleted. We will delete data based on a customer request to do so.

## Removing personal information from Launchable

Launchable stores information from Git commits. In that context, consider a developer's [Git profile information](https://git-scm.com/book/en/v2/Customizing-Git-Git-Configuration#_git_config) \(user name and email address\) as the personal information sent over to Launchable.

### Does Launchable support access requests and the ability to provide customer data in a readable and easily transferable format when required by the customer?

Yes. A customer just has to contact support to request this information.

### Does Launchable delete an individual's information for removal?

Since the service needs Git author information to function, we require you to unsubscribe from the service to delete this data.

### Can Launchable stop processing personal information when requested?

Since the service needs Git author information to function, we require you to unsubscribe from the service to delete this data.

