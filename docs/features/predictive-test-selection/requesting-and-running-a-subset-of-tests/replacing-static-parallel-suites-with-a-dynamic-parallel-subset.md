# Replacing static parallel suites with a dynamic parallel subset



### Replacing static parallel suites with a dynamic parallel subset

Some teams manually split their test suites into several "bins" to run them in parallel. This presents a challenge adopting Launchable, because you don't want to lose the benefit of parallelization.

Luckily, with **split subsets** you can replace your manually selected bins with automatically populated bins from a Launchable subset.

For example, let's say you currently run \~80 minutes of tests split coarsely into four bins and run in parallel across four workers:

* Worker 1: \~20 minutes of tests
* Worker 2: \~15 minutes of tests
* Worker 3: \~20 minutes of tests
* Worker 4: \~25 minutes of tests

With a split subset, you can generate a subset of the full 80 minutes of tests and then call Launchable once in each worker to get the bin of tests for that runner.

The high level flow is:

1. Request a subset of tests to run from Launchable by running `launchable subset` with the `--split` option. Instead of outputting a list of tests, the command will output a subset ID that you should save and pass into each runner.
2. Start up your parallel test worker, e.g. four runners from the example above
3. In each worker, request the bin of tests that worker should run. To do this, run `launchable split-subset` with:
   1. the `--subset-id` option set to the ID you saved earlier, and
   2. the `--bin` value set to `bin-number/bin-count`.
4. Run the tests in each worker.
5. After each run finishes in each worker, record test results using `launchable record tests` with the `--subset-id` option set to the ID you saved earlier.

In pseudocode:

```
# main
$ launchable record build --name $BUILD_ID --source src=.
$ launchable subset --split --confidence 90% --build $BUILD_ID bazel .
subset/12345

...

# worker 1
$ launchable split-subset --subset-id subset/12345 --bin 1/3 --rest rest.txt bazel > subset.txt
$ bazel test $(cat subset.txt)
$ launchable record tests --subset-id subset/12345 bazel .


# worker 2
$ launchable split-subset --subset-id subset/12345 --bin 2/3 --rest rest.txt bazel > subset.txt
$ bazel test $(cat subset.txt)
$ launchable record tests --subset-id subset/12345 bazel .

# worker 3
$ launchable split-subset --subset-id subset/12345 --bin 3/3 --rest rest.txt bazel > subset.txt
$ bazel test $(cat subset.txt)
$ launchable record tests --subset-id subset/12345 bazel .
```
