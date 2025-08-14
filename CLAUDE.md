# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the Smart Tests CLI - a Python-based command-line tool for intelligent test optimization. It provides predictive test selection, test subsetting, and comprehensive test result recording across multiple test runners and frameworks.

## Development Commands

This project uses [poethepoet](https://poethepoet.natn.io/) for task management. All development tasks are defined in the `[tool.poe.tasks]` section of `pyproject.toml` and can be run with `uv run poe <task>`.

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
uv run poe test

# Run tests with XML output
uv run poe test-xml

# Test Java components
bazel test ...
```

### Code Quality
```bash
# Lint code
uv run poe lint

# Format code (isort + autopep8)
uv run poe format

# Type checking
uv run poe type

# Lint with warnings (non-failing)
uv run poe lint-warn
```

### Building
```bash
# Build distribution packages
uv run poe build

# Update Java JAR component
./build-java.sh

# Install from source
uv run poe install
```

## Architecture Overview

### Core Components

**Main CLI Entry Point** (`smart_tests/__main__.py`):
- Typer-based command structure with global options (--dry-run, --log-level, --skip-cert-verification)
- Dynamic plugin loading system for test runners
- Application context management

**Command Structure**:
- `record` - Record test results, builds, commits, and sessions
- `subset` - Generate optimized test subsets using ML predictions
- `split_subset` - Split test subsets across multiple runners
- `verify` - Verify CLI setup and connectivity
- `inspect` - Inspect test and subset data
- `stats` - View test session statistics

**Test Runner Support** (`smart_tests/test_runners/`):
- 20+ supported test runners including pytest, jest, junit, bazel, cypress, etc.
- Each test runner implements standardized subset/record interfaces
- Automatic test path normalization and format conversion

**Core Utilities** (`smart_tests/utils/`):
- `launchable_client.py` - HTTP client for Launchable API
- `authentication.py` - Token-based authentication
- `session.py` - Test session management
- `git_log_parser.py` - Git commit ingestion
- `logger.py` - Structured logging with audit levels

### Test Runner Plugin System

Test runners are automatically loaded from `smart_tests/test_runners/*.py`. Each implements:
- `@smart_tests.subset` decorator for subset generation
- `@smart_tests.record` decorator for result recording
- Test path parsing and normalization
- Framework-specific configuration handling

### Java Component

The CLI includes a Java component (`src/main/java/`) for advanced Git commit processing:
- `CommitIngester.java` - Process Git history and diffs
- `GitHubActionsAuthenticator.java` - GitHub OIDC authentication
- Built with Bazel, packaged as `smart_tests/jar/exe_deploy.jar`

## Key Design Patterns

**Plugin Architecture**: Test runners are dynamically loaded modules that register themselves with the CLI core.

**Test Path Abstraction**: All test identifiers are normalized to a common `TestPath` format regardless of source framework.

**Session Management**: Test sessions group related test runs and provide context for subset generation.

**Dry Run Mode**: All commands support `--dry-run` to preview actions without sending data.

**File Path Normalization**: Automatic base path inference and relativization for portable test names.

## Testing Strategy

**Test Structure**:
- `tests/` - Unit tests mirroring source structure
- `tests/cli_test_case.py` - Base test class with mocked HTTP responses
- `tests/data/` - Test fixtures for each supported test runner
- XML test output via custom `test-runner/__main__.py`

**Test Execution**:
- Python unittest framework
- Mocked HTTP responses using `responses` library
- Comprehensive test data for 20+ test runners
- Both unit and integration test coverage

## Important Files

- `smart_tests/app.py` - Global application state and configuration
- `smart_tests/testpath.py` - Test path normalization and representation
- `smart_tests/commands/subset.py` - Core subset generation logic (670+ lines)
- `smart_tests/commands/helper.py` - Session management utilities
- `setup.cfg` - Package configuration and entry points
- `pyproject.toml` - Project metadata, dependencies and uv scripts

## Development Notes

- Python 3.13+ compatibility maintained
- Minimal external dependencies to avoid conflicts
- Extensive logging with configurable levels
- Comprehensive error handling and recovery
- Plugin system supports custom test runners via `--plugins` directory
