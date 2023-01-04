# Viewing time savings

You can view aggregate time savings from Predictive Test Selection on the **Time Savings** page. Time savings is the test execution time hypothetically saved by not executing all tests via Predictive Test Selection.

<figure><img src="../../.gitbook/assets/Time savings.png" alt=""><figcaption></figcaption></figure>

You can also view time savings for an individual test session in the **Subset Impact** section of a test session row. Generally speaking, though, this page explains the monthly report page.

## Month

Time Savings is aggregated by month based on the timestamp of the test session.

A test session is not closed until 7 days after creation. Until then, you can record test results. Time Savings values are only official after that point. This means that it takes 7 days for last month’s values to finalize, hence the yellow "Not Final Yet" badge.

## PTS Test Sessions (count)

This is the number of test sessions for which time savings was calculated. This number might be slightly lower than the total number of sessions that had subset requests.

Reasons for this include:

1. no tests were reported for the session
2. too many recorded tests had no past history, and/or
3. the test session had too many subset requests

## Durations

Time savings is “the test execution time hypothetically saved by not executing all tests \[using Predictive Test Selection]."

Since you didn't execute these tests, we do not know what the **actual** test time would be. However, based on the historical test executions, we can estimate the time it would have taken to execute.

{% hint style="info" %}
Launchable learns about test durations from the JUnit reports you record. Therefore they represent machine time.
{% endhint %}

We use **up to 90 days of test execution results** to estimate the time taken to execute a test.

### Total Duration Without Launchable

For each test session, we estimate how long your test sessions **would have** taken this long to run, in total. We use each [#input-test-list](../../concepts/subset.md#input-test-list "mention") to calculate this. Then we sum this for all test sessions.

This calculation handles various edge cases described in the below table.\


| Test recorded in test session? | Recorded in last 90 days? | Duration used in calculation                      |
| ------------------------------ | ------------------------- | ------------------------------------------------- |
| Yes                            | N/A                       | Actual recorded duration                          |
| No                             | Yes                       | Average duration over last 90 days                |
| No                             | No                        | Average duration of all tests in the test session |

### Total Duration With Launchable

Difference between [#time-saved](viewing-time-savings.md#time-saved "mention") and [#total-duration-without-launchable](viewing-time-savings.md#total-duration-without-launchable "mention").

Note that because all tests in the input list are included in [#total-duration-with-launchable](viewing-time-savings.md#total-duration-with-launchable "mention") -- even if they aren't recorded -- the recorded duration for a test session can be different than this value if you don't record all subset tests (or if tests are new).

### Time Saved

For each test session, we take the sum of the estimated duration of all unrecorded remainder/rest tests, using the average duration of each test over the last 90 days. This value is shown on each test session row in the Launchable webapp.

Then, for the Time Savings page, then we sum this for all test sessions grouped by month.
