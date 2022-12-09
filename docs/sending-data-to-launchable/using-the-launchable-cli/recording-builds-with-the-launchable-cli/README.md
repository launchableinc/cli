# Recording builds with the Launchable CLI

Each [test-session.md](../../../concepts/test-session.md "mention") is associated with a [build.md](../../../concepts/build.md "mention"). In particular, [predictive-test-selection](../../../features/predictive-test-selection/ "mention") selects tests based on the a Git changes in a build (among other data).

To send Git changes to Launchable using the CLI, run `launchable record build` before you create a build in your CI script:

```bash
launchable record build --name <BUILD NAME> --source src=<PATH TO SOURCE>
```

* With the `--name` option, you assign a unique identifier to this build. You will use this value later when you record test results. See [choosing-a-value-for-build-name.md](choosing-a-value-for-build-name.md "mention") for tips on choosing this value.
* The `--source` option points to the local copy of the Git repository (or repositories) used to produce this build, such as `.` or `src`.
  * See also [recording-builds-from-multiple-repositories.md](recording-builds-from-multiple-repositories.md "mention").

You can view your recorded builds on the **Builds** page of the Launchable dashboard at [app.launchableinc.com](https://app.launchableinc.com/). You can click into each build's details page to view info about it, including recorded test sessions.

<figure><img src="../../../.gitbook/assets/Builds v1.png" alt=""><figcaption></figcaption></figure>

After recording a build, you can start [recording-test-results-with-the-launchable-cli](../recording-test-results-with-the-launchable-cli/ "mention") against your builds.
