# Nose \(Python\)

## Installation

Install the Launchable plugin for Nose using PIP:

```text
$ pip install nose-launchable
```

## Usage

First, set a `LAUNCHABLE_TOKEN` environment variable containing your API key. \(For more info, see [Getting started](../getting-started.md).\)

Second, set the `LAUNCHABLE` environment variable to `on` to enable Launchable.

Then, invoke the plugin using the `--launchable` flag:

```bash
# enable Launchable
export LAUNCHABLE=on

# run tests with Launchable
nosetests --launchable
```

{% hint style="info" %}
The Nose plugin currently supports test _reordering._ Test _subsetting_ will be added in an upcoming release.
{% endhint %}

## Troubleshooting

If you encounter issues running Nose with the Launchable plugin, you can set the `LAUNCHABLE_DEBUG` environment variable to `1` before running tests to print debug logs.

```bash
# enable Launchable
export LAUNCHABLE=on

# enable debug logs
export LAUNCHABLE_DEBUG=1

# run tests with Launchable
nosetests --launchable
```

## Development

The Launchable Nose plugin is open source and [available on GitHub](https://github.com/launchableinc/nose-launchable). Pull requests are always appreciated!

