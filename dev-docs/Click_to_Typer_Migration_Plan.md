# Click to Typer Migration Plan

## Overview

This document outlines the migration plan for converting the Launchable CLI from Click to Typer. The migration will be a breaking change with no backward compatibility requirements, allowing for a clean and comprehensive conversion.

## Migration Scope Analysis

### Current Click Usage
- **51 files** using Click across the codebase
- **26 test runners** implementing Click decorators
- **6 main command groups**: record, subset, split_subset, verify, inspect, stats
- **Custom Click features**:
  - `GroupWithAlias` class for command aliases
  - 5 custom `ParamType` classes (Percentage, Duration, KeyValue, Fraction, DateTimeWithTimezone)
  - Context management via `@click.pass_context`
  - Dynamic plugin loading system

### Key Files Identified
- `launchable/__main__.py` - Main CLI entry point
- `launchable/app.py` - Application context management
- `launchable/utils/click.py` - Custom Click utilities and types
- `launchable/commands/` - All command implementations
- `launchable/test_runners/` - 26 test runner plugins

## Migration Approach

### Phase 1: Dependencies and Core Structure

#### 1.1 Update Dependencies
- **File**: `pyproject.toml`
- **Change**: Replace `click>=8.1` with `typer>=0.9.0`
- **Additional**: Add `types-typer` to dev dependencies

#### 1.2 Main CLI Application
- **File**: `launchable/__main__.py`
- **Changes**:
  - Replace `@click.group()` with `app = typer.Typer()`
  - Convert global options to Typer dependency injection
  - Update plugin loading mechanism for Typer compatibility
  - Replace `ctx.obj = Application()` with dependency injection pattern

#### 1.3 Application Context
- **File**: `launchable/app.py`
- **Changes**:
  - Adapt `Application` class for Typer's dependency injection
  - Create factory functions for dependency injection

#### 1.4 Custom Types Migration
- **File**: `launchable/utils/click.py` → `launchable/utils/typer_types.py`
- **Changes**:
  - Convert `PercentageType` to `Annotated[float, typer.Option()]` with validation
  - Convert `DurationType` to `Annotated[float, typer.Option()]` with validation
  - Convert `KeyValueType` to `Annotated[Tuple[str, str], typer.Option()]`
  - Convert `FractionType` to `Annotated[Tuple[int, int], typer.Option()]`
  - Convert `DateTimeWithTimezoneType` to `Annotated[datetime, typer.Option()]`
  - Migrate `GroupWithAlias` functionality to native Typer aliases

### Phase 2: Command Group Conversion

#### 2.1 Record Commands
- **File**: `launchable/commands/record/__init__.py`
- **Changes**:
  - Convert to Typer sub-application
  - Replace `GroupWithAlias` with standard Typer group
  - Update command registration pattern

#### 2.2 Subset Commands
- **File**: `launchable/commands/subset.py`
- **Changes**:
  - Convert complex option groups to Typer format
  - Update `@click.group()` to Typer sub-app
  - Migrate custom option types

#### 2.3 Other Command Groups
- **Files**: 
  - `launchable/commands/verify.py`
  - `launchable/commands/split_subset.py`
  - `launchable/commands/stats/__init__.py`
  - `launchable/commands/inspect/__init__.py`
- **Changes**: Convert each command group following the same pattern

### Phase 3: Test Runner Plugin Conversion

#### 3.1 Plugin System Updates
- **Files**: All files in `launchable/test_runners/`
- **Count**: 26 test runner implementations
- **Changes**:
  - Replace `@click.command()` with `@app.command()`
  - Convert `@click.option()` to `typer.Option()`
  - Convert `@click.argument()` to `typer.Argument()`
  - Update decorator patterns for `@launchable.subset` and `@launchable.record`

#### 3.2 Dynamic Loading
- **File**: `launchable/__main__.py` (plugin loading section)
- **Changes**: Ensure dynamic plugin loading works with Typer's command registration

### Phase 4: Tests and Build System

#### 4.1 Test Updates
- **Files**: All files in `tests/`
- **Changes**:
  - Replace Click testing utilities with Typer's `TestClient`
  - Update test fixtures and mocks
  - Verify CLI behavior remains consistent

#### 4.2 Build System
- **Files**: CI/CD configurations, build scripts
- **Changes**: Verify compatibility with new Typer-based CLI

## Click to Typer Mapping Reference

### Basic Patterns
```python
# Click
@click.group()
@click.option('--verbose', is_flag=True)
def cli(verbose):
    pass

# Typer
app = typer.Typer()

@app.command()
def cli(verbose: bool = typer.Option(False, "--verbose")):
    pass
```

### Context Management
```python
# Click
@click.pass_context
def command(ctx):
    app = ctx.obj

# Typer
def command(app: Application = typer.Depends(get_application)):
    pass
```

### Custom Types
```python
# Click
@click.option('--target', type=PERCENTAGE)

# Typer
def command(target: Annotated[float, typer.Option()] = None):
    # Validation handled by custom validator
```

## Migration Benefits

1. **Modern Python**: Better type hints and IDE support
2. **Automatic Documentation**: Better help generation
3. **Simpler Code**: Less boilerplate for common patterns
4. **Better Testing**: More intuitive testing framework
5. **Active Development**: Typer is actively maintained

## Risks and Mitigation

### Risks
1. **Plugin System Compatibility**: Dynamic loading may need adjustments
2. **Custom Type Complexity**: Some custom types may need rework
3. **Test Coverage**: Ensuring all CLI behavior is preserved

### Mitigation
1. **Comprehensive Testing**: Run full test suite after each phase
2. **Gradual Migration**: Phase-by-phase approach allows for validation
3. **Documentation**: Update all CLI documentation post-migration

## Estimated Timeline

- **Phase 1**: 1 day (Dependencies and core structure)
- **Phase 2**: 1 day (Command groups)
- **Phase 3**: 1.5 days (Test runners)
- **Phase 4**: 0.5 day (Tests and validation)
- **Total**: 4 days

## Success Criteria

1. All CLI commands work identically to Click version
2. All tests pass
3. Plugin system continues to work
4. Documentation is updated
5. CI/CD pipeline passes
6. Performance is maintained or improved

## Next Steps

1. Get approval for migration plan
2. Create feature branch for migration
3. Execute Phase 1 and validate
4. Continue with subsequent phases
5. Comprehensive testing and validation
6. Documentation updates
7. Merge to main branch
