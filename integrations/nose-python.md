# Nose \(Python\)

## Installation

The Nose plugin can be installed with the `pip` command:

```text
pip install nose-launchable
```

## Usage

```text
nosetests --launchable
```

In addition to specifying the `--launchable` flag, you need to set the following environment variables in your environment. These values should be provided from Launchable.

| Key | Description |
| :--- | :--- |
| `LAUNCHABLE_TOKEN` | A token to access Launchable API |
| `LAUNCHABLE_DEBUG` | Prints out debug logs |

## Development

The Launchable Nose plugin is open source and available on GitHub here:

[https://github.com/launchableinc/nose-launchable](https://github.com/launchableinc/nose-launchable)

Pull requests are always appreciated.

