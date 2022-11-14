# Zero Input Subsetting

Normally, when you run `launchable subset`, the Launchable CLI gathers the full list of tests on the client side and submits it with the subset request. (Highlighted in gray)

The subset request then returns a list of tests to **include** (i.e. run these tests):

<figure><img src="../../../.gitbook/assets/image (2).png" alt=""><figcaption><p>Regular subsetting approach</p></figcaption></figure>

This strategy is problematic in some cases, which is why we've created a complementary approach called **Zero Input Subsetting**. With this approach, the CLI does not have to gather and submit the full list of tests. Instead, the server generates the full list of tests from the last 2 weeks of recorded sessions. And to ensure new tests are run, the CLI outputs exclusion rules instead of inclusion rules.

{% hint style="warning" %}
Zero Input Subsetting works better with some [#test-session-layouts](../../../concepts/test-session.md#test-session-layouts "mention") than others, so contact your Customer Success Manager before you start using this feature. We're here to help!&#x20;
{% endhint %}

You can adopt this approach by adding two options to `launchable subset`:

* `--get-tests-from-previous-sessions`, and
* `--output-exclusion-rules`

The subset request then returns a list of tests to **exclude** (i.e. **don't** run these tests):

<figure><img src="../../../.gitbook/assets/image (1).png" alt=""><figcaption><p>Zero input subsetting</p></figcaption></figure>

{% hint style="info" %}
We in the process of updating the rest of the documentation to include this approach as an option. More to come!
{% endhint %}
