# pipenv → uv Migration Guide

## Overview

Migrating the Launchable CLI from pipenv to uv will achieve significant performance improvements (10-100x faster) in dependency resolution and installation. By supporting only the latest Python versions, we'll also improve maintainability.

## Migration Benefits

- **Performance Improvement**: 10-100x faster dependency resolution
- **CI/CD Acceleration**: Dramatically reduced installation times
- **Enhanced Developer Experience**: Single tool for Python + dependencies + virtual environments
- **Better Dependency Resolution**: More accurate and faster resolution algorithms
- **Modern Tooling**: Compliance with latest Python packaging standards

## Migration Steps

### Phase 1: Preparation & Validation

#### 1.1 Install uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# または pip経由
pip install uv
```

#### 1.2 Backup Current Environment
```bash
# Record current dependencies
pipenv graph > pipenv_dependencies_backup.txt
pipenv requirements > requirements_backup.txt
pipenv requirements --dev > requirements_dev_backup.txt
```

#### 1.3 Verify Compatibility with uv
```bash
# Test dependency resolution with uv
uv pip compile --python-version 3.12 <(pipenv requirements) > test_requirements.txt
uv pip compile --python-version 3.12 <(pipenv requirements --dev) > test_requirements_dev.txt
```

### Phase 2: Configuration File Conversion

#### 2.1 Update pyproject.toml

Add the following to the existing `pyproject.toml`:

```toml
[project]
name = "launchable"
authors = [
    {name = "Launchable, Inc.", email = "info@launchableinc.com"}
]
description = "Launchable CLI"
readme = "README.md"
license = {text = "Apache Software License v2"}
requires-python = ">=3.12"
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: Apache Software License",
    "Operating System :: OS Independent",
]
dependencies = [
    "click>=8.1,<8.2",
    "requests>=2.25",
    "urllib3>=1.26",
    "junitparser>=2.0.0",
    "setuptools",
    "more-itertools>=7.1.0",
    "python-dateutil",
    "tabulate",
]
dynamic = ["version"]

[project.urls]
Homepage = "https://launchableinc.com/"
Repository = "https://github.com/launchableinc/cli"

[project.scripts]
launchable = "launchable.__main__:main"

[tool.uv]
dev-dependencies = [
    "flake8",
    "autopep8<=1.7.0",
    "isort",
    "mypy<1.16.0",
    "pre-commit",
    "responses",
    "types-click",
    "types-pkg_resources==0.1.3",
    "types-python-dateutil",
    "types-requests",
    "types-tabulate",
    "lxml<=5.2.2",
    "unittest-xml-reporting",
]

[tool.uv.scripts]
build = "python -m build"
format = "/bin/bash -c 'isort -l 130 --balanced launchable/*.py tests/*.py && autopep8 --in-place --recursive --aggressive --experimental --max-line-length=130 --verbose launchable/ tests/'"
install = "pip install -U ."
lint = "flake8 --count --ignore=C901,E741,F401 --show-source --max-line-length=130 --statistics launchable/ tests/"
lint-warn = "flake8 --count --exit-zero --max-complexity=15 --max-line-length=130 --statistics launchable/ tests/"
test = "python -m unittest"
test-xml = "python -m test-runner"
type = "mypy launchable tests"

[build-system]
requires = ["setuptools>=45", "wheel", "setuptools_scm"]
build-backend = "setuptools.build_meta"

[tool.setuptools_scm]
```

#### 2.2 Adjust setup.cfg

Remove dependencies from the `[options]` section in `setup.cfg` (migrated to pyproject.toml):

```cfg
[metadata]
name = launchable
author = Launchable, Inc.
author_email = info@launchableinc.com
license = Apache Software License v2
description = Launchable CLI
url = https://launchableinc.com/
long_description = file: README.md
long_description_content_type = text/markdown
classifiers =
    Programming Language :: Python :: 3
    License :: OSI Approved :: Apache Software License
    Operating System :: OS Independent

[options]
packages = find:
python_requires = >=3.12

[options.package_data]
launchable = jar/exe_deploy.jar
```

### Phase 3: Development Environment Migration

#### 3.1 Create Virtual Environment
```bash
# Deactivate existing pipenv environment
exit  # Exit from pipenv shell

# Create new virtual environment with uv
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate  # Windows
```

#### 3.2 Install Dependencies
```bash
# Install production dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e .[dev]
# or
uv sync --dev
```

#### 3.3 Verify Functionality
```bash
# Test each script
uv run lint
uv run type
uv run test
uv run format
uv run build
```

### Phase 4: CI/CD Updates

#### 4.1 Update GitHub Actions Workflows

Update `.github/workflows/python-package.yml`:

```yaml
name: Python package

on:
  workflow_dispatch:
  push:
    branches: [ main ]
    paths-ignore:
      - 'WORKSPACE'
      - 'src/**'
  pull_request:
    branches: [ main ]
    paths-ignore:
      - 'WORKSPACE'
      - 'src/**'
  schedule:
    - cron: '0 9 * * *'

env:
  LAUNCHABLE_ORGANIZATION: "launchableinc"
  LAUNCHABLE_WORKSPACE: "cli"
  GITHUB_PULL_REQUEST_URL: ${{ github.event.pull_request.html_url }}
  GITHUB_PR_HEAD_SHA: ${{ github.event.pull_request.head.sha }}

permissions:
  id-token: write
  contents: read

jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-22.04, windows-latest]
        python-version: ["3.12"]

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0
    
    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        enable-cache: true
        cache-dependency-glob: "uv.lock"
    
    - name: Set up Python ${{ matrix.python-version }}
      run: uv python install ${{ matrix.python-version }}
    
    - name: Set up JDK 1.8
      uses: actions/setup-java@v4
      with:
        java-version: 8
        distribution: 'temurin'
    
    - name: Install dependencies
      run: uv sync --dev
    
    - name: Build
      run: |
        uv pip list
        uv run build
        uv run install
    
    - name: Type check
      run: uv run type
    
    - name: Lint with flake8
      run: uv run lint
    
    - name: Pull request validation
      run: |
        # Install Launchable CLI from this repo's code
        uv pip install . > /dev/null

        set -x

        launchable verify

        # Tell Launchable about the build you are producing and testing
        launchable record build --name ${GITHUB_RUN_ID}

        launchable record session --build ${GITHUB_RUN_ID} --flavor os=${{ matrix.os }} --flavor python=${{ matrix.python-version }} > session.txt

        # Find 25% of the relevant tests to run for this change
        find tests -name test_*.py | grep -v tests/data | launchable subset --target 25% --session $(cat session.txt) --rest launchable-remainder.txt file > subset.txt

        function record() {
          # Record test results
          LAUNCHABLE_SLACK_NOTIFICATION=true launchable record tests --session $(cat session.txt) file test-results/*.xml
        }

        trap record EXIT

        # Test subset of tests
        uv run test-xml $(tr '\r\n' '\n' < subset.txt)

        # Test rest of tests
        uv run test-xml $(tr '\r\n' '\n' < launchable-remainder.txt)
      shell: bash
```

#### 4.2 Update python-publish.yml

```yaml
# Update the pypi job section
pypi:
  needs: tagpr
  if: needs.tagpr.outputs.tag != '' || github.event_name == 'workflow_dispatch'
  runs-on: ubuntu-22.04

  steps:
  - uses: actions/checkout@v4
    with:
      fetch-depth: 0
  
  - name: Install uv
    uses: astral-sh/setup-uv@v3
  
  - name: Set up Python
    run: uv python install 3.12
  
  - name: Build package
    run: uv build
  
  - name: Publish to PyPI
    uses: pypa/gh-action-pypi-publish@release/v1
    with:
      user: __token__
      password: ${{ secrets.PYPI_API_TOKEN }}

  # Rest remains the same...
```

### Phase 5: Documentation Updates

#### 5.1 Update README.md Development Section

```markdown
# Development

## Preparation

We recommend uv for dependency management:

```shell
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev
```

## Load development environment

```shell
# Activate virtual environment
source .venv/bin/activate
# or use uv run for individual commands
uv run <command>
```

## Run tests

```shell
uv run test
```

## Add dependency

```shell
# Add runtime dependency
uv add some-package

# Add development dependency  
uv add --dev some-dev-package
```
```

#### 5.2 Update CLAUDE.md

Update the development commands section:

```markdown
### Environment Setup
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync --dev

# Install pre-commit hooks for code formatting
uv run pre-commit install
```

### Testing
```bash
# Run all tests
uv run test

# Run tests with XML output
uv run test-xml

# Test Java components
bazel test ...
```

### Code Quality
```bash
# Lint code
uv run lint

# Format code (isort + autopep8)
uv run format

# Type checking
uv run type

# Lint with warnings (non-failing)
uv run lint-warn
```

### Building
```bash
# Build distribution packages
uv run build

# Update Java JAR component
./build-java.sh

# Install from source
uv run install
```
```

### Phase 6: Execute Migration

#### 6.1 Create Branch and Execute Migration
```bash
# Create migration branch
git checkout -b migrate-to-uv

# Remove old files
rm Pipfile Pipfile.lock

# Commit changes
git add .
git commit -m "Migrate from pipenv to uv

- Update pyproject.toml with project metadata and dependencies
- Add uv configuration and scripts
- Update GitHub Actions workflows for uv
- Update documentation (README.md, CLAUDE.md)
- Remove Pipfile and Pipfile.lock

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"
```

#### 6.2 Test and Review
```bash
# Run tests locally
uv run test
uv run lint  
uv run type

# Push for CI/CD testing
git push -u origin migrate-to-uv
```

#### 6.3 Create Pull Request
- Detailed explanation of changes
- Explanation of migration reasons and benefits
- Share verification results
- Request team review

## Post-Migration Benefits

1. **Performance**: 10-100x faster dependency resolution and installation
2. **Simplification**: Python version management integrated into uv
3. **Modernization**: Compliance with latest Python packaging standards
4. **CI/CD Efficiency**: Significant reduction in build times

## Troubleshooting

### Common Issues

1. **Dependency Conflicts**
   ```bash
   uv pip compile --upgrade
   ```

2. **Virtual Environment Issues**
   ```bash
   rm -rf .venv
   uv venv
   ```

3. **Stale Cache Issues**
   ```bash
   uv cache clean
   ```

## Rollback Plan

If issues occur during migration:

1. Restore existing Pipfile from git history
2. Rebuild pipenv environment
3. Revert CI/CD workflows

```bash
git checkout main
git checkout HEAD~1 -- Pipfile Pipfile.lock
pipenv install --dev
```
