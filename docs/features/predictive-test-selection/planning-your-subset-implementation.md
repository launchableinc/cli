# Planning your subset implementation

## Preparing your pipeline for subsetting

Depending on your goal, you might need to make a few changes to your pipeline to adopt subsetting.&#x20;

### Goal: Run a subset of tests at the same stage of your software delivery lifecycle

After subsetting your tests, you should make sure to run the full suite of tests at _some point_ later in your pipeline.

For example, once you start running a subset of an integration test suite that runs on pull requests, you should make sure to run the **full** integration test suite after a PR is merged (and record the outcome of those runs with `launchable record tests`).

![Run the full suite after merging](<../../.gitbook/assets/In place@2x.png>)

### Goal: Run a subset of tests earlier in your software delivery lifecycle ("shift left")

If your goal is to run a short subset of a long test suite earlier in the development process, then you may need to set up a new pipeline to run tests in that development phase. For example, if you currently run a long nightly test suite, and you want to run a subset of that suite every hour, you may need to create a pipeline to build, deploy, and run the subset if one doesn't exist already.

You'll also want to continue running the full test suite every night (and recording the outcome of those runs with `launchable record tests`).

![Shift nightly tests left](<../../.gitbook/assets/Shift left@2x.png>)

##
