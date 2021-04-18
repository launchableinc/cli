# Recording builds from multiple repositories

If you produce a build by combining code from several repositories, invoke`launchable record build` with multiple `--source` options to denote them.

To differentiate them, provide a label for each repository in the form of `LABEL=PATH`:

```bash
# record the build
launchable record build --name <BUILD NAME> --source main=./main_repo --source lib=./lib_repo

# create the build
bundle install
```

{% hint style="info" %}
Note: `record build` automatically recognizes [Git submodules](https://www.git-scm.com/book/en/v2/Git-Tools-Submodules), so there’s no need to explicitly declare them.
{% endhint %}

