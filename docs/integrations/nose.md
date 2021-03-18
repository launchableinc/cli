# Nose \(Python\)

## Installation

Install the Launchable plugin for Nose using PIP:

```bash
$ pip install nose-launchable
```

## Subsetting

For subsetting, you need an additional flag called `--launchable-subset-target`, which specifies the percentage of subsetting in the total execution time.

For example, `--launchable-subset-target 20` means Launchable optimizes and subsets the tests so that the test duration will be 20% of the total test duration.

```bash
# subset tests with Launchable
nosetests --launchable-subset --launchable-subset-target 20
```

## Recording test results

## Troubleshooting

If you encounter issues running Nose with the Launchable plugin, you can set the `LAUNCHABLE_DEBUG` environment variable to `1` before running tests to print debug logs.

```bash
# enable debug logs
export LAUNCHABLE_DEBUG=1

# run tests with Launchable
nosetests --launchable
```

## Development

The Launchable Nose plugin is open source and [available on GitHub](https://github.com/launchableinc/nose-launchable). Pull requests are always appreciated!

