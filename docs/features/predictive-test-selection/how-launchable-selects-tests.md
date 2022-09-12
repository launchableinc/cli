# How Launchable selects tests

After you start [sending-data-to-launchable](../../sending-data-to-launchable/ "mention"), Launchable starts training a machine learning model for your workspace using its data. Later, you can use this model to select tests to run. This page covers this process.

## Model training

A model's goal is to predict which tests are most likely to fail in the shortest amount of testing time. Predictive Test Selection is designed to find failures quickly so that you can validate changes faster: is this change going to cause a test failure, or is it good to go?

Launchable trains models and selects tests to run based on a variety of factors. Each model is trained using lots of extracted metadata from your test results and code changes over time, including:

* Test execution history
* Test characteristics
* Test name/path and file name/path similarity
* Change characteristics
* Flavors

<figure><img src="../../.gitbook/assets/2022-09-12 model training diagram.png" alt=""><figcaption><p>Model training uses various historical data</p></figcaption></figure>

## Test selection

Once your workspace's model is trained, you can start requesting dynamic subsets of tests for your builds.

### High level process

Every time your CI system requests a subset of tests to run for a build, it's essentially asking the PTS service a question:

> Given
>
> 1\) the tests in my test suite,\
> 2\) the changes in the build we're testing, and\
> 3\) the flavors (environments) we're testing under,
>
> which tests from the test suite (1) should we run/not run in order to find out if the change is going to cause a test failure?

To do this, for each subset request, the PTS service completes a two step process:

1. Prioritizing all tests based on the request's inputs
2. Creating a subset of tests from the full prioritized test list

<figure><img src="../../.gitbook/assets/2022-09-12 full subset interaction diagram.png" alt=""><figcaption></figcaption></figure>

The following sections explore this process in more detail.

### Inputs

The inputs for a subset request are:

1. **Full test suite** - The list of the tests in your test suite you would normally run in a full test execution. This is what's being prioritized and subsetted
2. **Changes** - The changes in the build being tested
3. **Flavors** - The environment(s) in which the tests are running
4. **Optimization target** - The factor that determines the size (in terms of test duration) of the subset to create to satisfy an aggregate goal (e.g. confidence, duration)

### Test prioritization

The first three inputs (Full test suite, Changes, Flavors) are fed into the test prioritization step.

Here, we're basically asking the model to prioritize the list of tests for us. The model prioritizes tests based on the factors described above in **Model training**.

<figure><img src="../../.gitbook/assets/2022-09-12 test prioritization.png" alt=""><figcaption></figcaption></figure>

Now let's cover a few common questions about test prioritization.

#### Is a model a mapping between files and tests?

A model is not a simple mapping of files to tests. Although file paths and test paths _are_ compared for similarity, it's important to point out that Launchable extracts _characteristics_ from changes in a way that makes each change more generally useful for training and inference. Additionally, the historical behavior of the tests themselves (without incorporating changes) are also an important factor.

#### What if I'm making changes in an area of my codebase that I haven't changed for a while?

Because Launchable extracts _characteristics_ from changes in a way that makes each change more generally useful for training and inference, your workspace's model can make predictions for changes made in logical areas of your codebase that it hasn't "seen" yet. This is a massive benefit!

#### The tests Launchable selected relate to a different logical area of my codebase than the change. Why did these tests get prioritized?

Sometimes, a model may may prioritize tests that, on-the-surface, may not _appear_ to relate to the logical area that is being changed.

In this case, it's important to remember

1. the model learns from much more than just the relationship between files and changes, such as the tests' execution history and the other factors described above, which may outweigh the logical relationship
2. the model's goal is to prioritize tests that fail - i.e. tests that don't fail don't usually get prioritized!
3. given two tests with the same likelihood of failure, the model will prioritize the shorter test over the longer one
4. because of test runner constraints, in many cases tests must be prioritized at a higher altitude (e.g. class instead of testcase) which can impact prioritization

### Subset creation

Then, the prioritized list of tests is combined with the subset request's Optimization target to create a subset of tests. This process essentially cuts the prioritized list into two chunks: the subset, and the remainder.

For example, if your optimization target is 20% duration, and the estimated duration of the prioritized full test suite is 100 minutes, then the subset will include the top tests from the prioritized list until those tests add up to 20 minutes of estimated duration.

<figure><img src="../../.gitbook/assets/2022-09-12 subset creation.png" alt=""><figcaption></figcaption></figure>

Similarly, some common questions:

#### If I make a small change, will my subset of tests take less time to run? Similarly, if I make a large change, will my subset take longer to run?

Assuming the same 1) full test suite, 2) optimization target, and 3) model, two subset requests should take about the same amount of time to run.

Models are regularly re-trained with the latest data, in practice this means that a given day's subsets should all be about the same length, regardless of changes. The duration is informed by the Confidence curve.

