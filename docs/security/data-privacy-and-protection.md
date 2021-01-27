---
description: Your data is our highest priority
---

# Data Privacy and Protection

### Purpose and use of collected information

Launchable’s predictive test selection service learns the relationship between code changes and the test cases impacted by those changes.

#### Does Launchable use the personal information for any purpose outside providing the services?

No

#### Does Launchable use any anonymized or aggregate data for any independent purpose outside of providing the services?

No

## Specifics on the data sent to Launchable

#### Does Launchable need access to the source code?

The actual content of your source code is not needed, only metadata about changes.

#### What data is sent over to Launchable?

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

## Data storage and retention

#### Does Launchable encrypt personal information?

We encrypt data in transit and at rest.

#### How does Launchable store customer data?

Launchable is a multi-tenant SaaS product. Each customer’s data is kept separate from each other.

#### Where is the customer data stored specifically?

Launchable is hosted on AWS and use US-West as our region.

#### How long is customer data retained by Launchable? Will customer data be deleted or returned at the end of the engagement?

The customer has an option to get their data deleted. We delete the data based on customer request to do so.

## Removing personal information from Launchable

Launchable uses `git ids` and in that context consider the developer author id as the personal information sent over to Launchable.

#### Does Launchable support access requests and the ability to provide customer data in a readable and easily transferable format when required by the customer?

Yes - a customer has to reach out Launchable support to ask for the information.

#### Does Launchable delete an individuals information for removal?

Since we work with git author id, we require you to unsubscribe from the service to delete this data.

#### Can Launchable stop processing personal information when requested?

Since we work with git author id we require you to unsubscribe from the service to stop processing this data.

