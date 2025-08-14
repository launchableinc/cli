# Launchable CLI v1

## `record build`
* `--name`
  * help text: `build name`
  * required: yes
* `--source`
  * help text: `path to local Git workspace, optionally prefixed by a label. like --source path/to/ws or --source main=path/to/ws`
  * required: no
* `--max-days`
  * help text: `the maximum number of days to collect commits retroactively`
  * required: no
* `--no-submodules`
  * help text: `stop collecting information from Git Submodules`
  * required: no
* `--no-commit-collection`
  * help text: `do not collect commit data. This is useful if the repository is a shallow clone and the RevWalk is not possible. The commit data must be collected with a separate fully-cloned repository.`
  * required: no
* `--scrub-pii`
  * help text: `Scrub emails and names`
  * required: no
* `--commit`
  * help text: `set repository name and commit hash when you use --no-commit-collection option`
  * required: no
* `--link`
  * help text: `Set external link of title and url`
  * required: no
* `--branch`
  * help text: `Set repository name and branch name when you use --no-commit-collection option. Please use the same repository name with a commit option`
  * required: no
* `--timestamp`
  * help text: `Used to overwrite the build time when importing historical data. Note: Format must be ```YYYY-MM-DDThh:mm:ssTZD``` or ```YYYY-MM-DDThh:mm:ss``` (local timezone applied)`
  * required: no

## `record commit`
* `--source`
  * help text: `repository path`
  * required: no
* `--executable`
  * help text: `[Obsolete] it was to specify how to perform commit collection but has been removed`
  * required: no
* `--max-days`
  * help text: `the maximum number of days to collect commits retroactively`
  * required: no
* `--scrub-pii`
  * help text: `[Deprecated] Scrub emails and names`
  * required: no
* `--import-git-log-output`
  * help text: `import from the git-log output`
  * required: no

## `record session`
* `--build`
  * help text: `build name`
  * required: no
* `--save-file/--no-save-file`
  * help text: `save session to file`
  * required: no
* `--flavor`
  * help text: `flavors`
  * required: no
* `--observation`
  * help text: `enable observation mode`
  * required: no
* `--link`
  * help text: `Set external link of title and url`
  * required: no
* `--no-build`
  * help text: `If you want to only send test reports, please use this option`
  * required: no
* `--session-name`
  * help text: `test session name`
  * required: no
* `--lineage`
  * help text: `Set lineage name. A lineage is a set of test sessions grouped and this option value will be used for a lineage name.`
  * required: no
* `--test-suite`
  * help text: `Set test suite name. A test suite is a collection of test sessions. Setting a test suite allows you to manage data over test sessions and lineages.`
  * required: no
* `--timestamp`
  * help text: `Used to overwrite the session time when importing historical data. Note: Format must be ```YYYY-MM-DDThh:mm:ssTZD``` or ```YYYY-MM-DDThh:mm:ss``` (local timezone applied)`

## `record tests`
* `--base`
  * help text: `(Advanced) base directory to make test names portable`
  * required: no
* `--session`
  * help text: `Test session ID`
  * required: no
* `--build`
  * help text: `build name`
  * required: no
* `--subset-id`
  * help text: `subset_id`
  * required: no
* `--post-chunk`
  * help text: `Post chunk`
  * required: no
* `--flavor`
  * help text: `flavors`
  * required: no
* `--no-base-path-inference`
  * help text: `Do not guess the base path to relativize the test file paths. By default, if the test file paths are absolute file paths, it automatically guesses the repository root directory and relativize the paths. With this option, the command doesn't do this guess work. If --base_path is specified, the absolute file paths are relativized to the specified path irrelevant to this option. Use it if the guessed base path is incorrect.`
  * required: no
* `--report-paths`
  * help text: `Instead of POSTing test results, just report test paths in the report file then quit. For diagnostics. Use with --dry-run`
  * required: no
* `--group`
  * help text: `Grouping name for test results`
  * required: no
* `--allow-test-before-build`
  * help text: ``
  * required: no
* `--link`
  * help text: `Set external link of title and url`
  * required: no
* `--no-build`
  * help text: `If you want to only send test reports, please use this option`
  * required: no
* `--session-name`
  * help text: `test session name`
  * required: no
* `--lineage`
  * help text: `Set lineage name. This option value will be passed to the record session command if a session isn't created yet.`
  * required: no
* `--test-suite`
  * help text: `Set test suite name. This option value will be passed to the record session command if a session isn't created yet.`
  * required: no
* `--timestamp`
  * help text: `Used to overwrite the test executed times when importing historical data. Note: Format must be ```YYYY-MM-DDThh:mm:ssTZD``` or ```YYYY-MM-DDThh:mm:ss``` (local timezone applied)`
  * required: no

## `subset`
* `--target`
  * help text: `subsetting target from 0% to 100%`
  * required: no
* `--time`
  * help text: `subsetting by absolute time, in seconds e.g) 300, 5m`
  * required: no
* `--confidence`
  * help text: `subsetting by confidence from 0% to 100%`
  * required: no
* `--goal-spec`
  * help text: `subsetting by programmatic goal definition`
  * required: no
* `--session`
  * help text: `Test session ID`
  * required: no
* `--base`
  * help text: `(Advanced) base directory to make test names portable`
  * required: no
* `--build`
  * help text: `build name`
  * required: no
* `--rest`
  * help text: `Output the subset remainder to a file, e.g. --rest=remainder.txt`
  * required: no
* `--flavor`
  * help text: `flavors`
  * required: no
* `--split`
  * help text: `split`
  * required: no
* `--no-base-path-inference`
  * help text: `Do not guess the base path to relativize the test file paths. By default, if the test file paths are absolute file paths, it automatically guesses the repository root directory and relativize the paths. With this option, the command doesn't do this guess work. If --base_path is specified, the absolute file paths are relativized to the specified path irrelevant to this option. Use it if the guessed base path is incorrect.`
  * required: no
* `--ignore-new-tests`
  * help text: `Ignore tests that were added recently. NOTICE: this option will ignore tests that you added just now as well`
  * required: no
* `--observation`
  * help text: `enable observation mode`
  * required: no
* `--get-tests-from-previous-sessions`
  * help text: `get subset list from previous full tests`
  * required: no
* `--output-exclusion-rules`
  * help text: `outputs the exclude test list. Switch the subset and rest.`
  * required: no
* `--non-blocking`
  * help text: `Do not wait for subset requests in observation mode.`
  * required: no
* `--ignore-flaky-tests-above`
  * help text: `Ignore flaky tests above the value set by this option. You can confirm flaky scores in WebApp`
  * required: no
* `--link`
  * help text: `Set external link of title and url`
  * required: no
* `--no-build`
  * help text: `If you want to only send test reports, please use this option`
  * required: no
* `--session-name`
  * help text: `test session name`
  * required: no
* `--lineage`
  * help text: `Set lineage name. This option value will be passed to the record session command if a session isn't created yet.`
  * required: no
* `--prioritize-tests-failed-within-hours`
  * help text: `Prioritize tests that failed within the specified hours; maximum 720 hours (= 24 hours * 30 days)`
  * required: no
* `--prioritized-tests-mapping`
  * help text: `Prioritize tests based on test mapping file`
  * required: no
* `--test-suite`
  * help text: `Set test suite name. This option value will be passed to the record session command if a session isn't created yet.`
  * required: no

## `record attachment`
* `--session`
  * help text: `Test session ID`
  * required: no

## `verify`
* no options

## `split-subset`
* `--subset-id`
  * help text: `subset id`
  * required: yes
* `--bin`
  * help text: `bin`
  * required: no
* `--rest`
  * help text: `output the rest of subset`
  * required: no
* `--base`
  * help text: `(Advanced) base directory to make test names portable`
  * required: no
* `--same-bin`
  * help text: `(Advanced) gather specified tests into same bin`
  * required: no
* `--split-by-groups`
  * help text: `split by groups that were set by launchable record tests --group`
  * required: no
* `--split-by-groups-with-rest`
  * help text: `split by groups that were set by launchable record tests --group and produces with rest files`
  * required: no
* `--split-by-groups-output-dir`
  * help text: `split results output dir`
  * required: no
* `--output-exclusion-rules`
  * help text: `outputs the exclude test list. Switch the subset and rest.`
  * required: no

## `inspect subset`
* `--subset-id`
  * help text: `subset id`
  * required: yes
* `--json`
  * help text: `display JSON format`
  * required: no

## `inspect tests`
* `--test-session-id`
  * help text: `test session id`
  * required: no
* `--json`
  * help text: `display JSON format`
  * required: no

## `stats test-sessions`
* `--days`
  * help text: `How many days of test sessions in the past to be stat`
  * required: no
* `--flavor`
  * help text: `flavors`
  * required: no
