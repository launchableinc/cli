# Observing subset behavior

## Observation mode

{% hint style="info" %}
Coming soon!
{% endhint %}

## Inspecting subset details

You can use `launchable inspect subset` to inspect the details of a specific subset, including rank and expected duration. This is useful for verifying that you passed the correct tests or test directory path(s) into `launchable subset`.

The output from `launchable subset` includes a tip to run `launchable inspect subset`:

```bash
$ launchable subset --build 123 --confidence 90% minitest test/*.rb > subset.txt

< summary table >

Run `launchable inspect subset --subset-id 26876` to view full subset details
```

Running that command will output a table containing a row for each test including:

* Rank/order
* Test identifier
* Whether the test was included in the subset
* Launchable's estimated duration for the test
  * Tests with a duration of `.001` seconds were not recognized by Launchable

{% hint style="success" %}
Note that the hierarchy level of the items in the list depends on the test runner in use.

For example, since Maven can accept a list of test _classes_ as input, `launchable inspect subset` will output a prioritized list of test _classes_. Similarly, since Cypress can accept a list of test _files_ as input, `launchable inspect subset` will output a list of prioritized test _files_. (And so on.)
{% endhint %}
