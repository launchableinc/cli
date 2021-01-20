# Coding style
Code should follow [pep8](https://www.python.org/dev/peps/pep-0008/). To check coding style, this repo using `[flake8](https://flake8.pycqa.org/)` on Github Actions.
`[autopep8](https://pypi.org/project/autopep8/)` might help you fixing your code's style.

# Development
You can use Python's `-m` option to launch module directly.
```shell
python3 -m launchable record commit
```

# Design Philosophy
- **Dependencies**: Launchable needs to run with varying environments of users. So when we need to
  reduce dependencies to other packages or tools installed on the system. For example, Python packages
  we depend on and their version constraints might conflict with what other Python packages specifies.
  Some libraries have native components, which need to be built during `pip install` and that adds to
  the burden, too.
- **Extensibility**: Test runners people use are all over the map. To provide 1st class support for those
  while keeping the code DRY, CLI has two layers. The core layer that defines a properly abstracted
  generic logic, and tool specific "integration" layers that glue the core layer and different tools.
