# Click-to-Typer Migration: Remaining Tasks

## Overview
This document outlines the remaining tasks for migrating the Launchable CLI from Click to Typer. The migration follows a static code conversion approach, avoiding dynamic wrapper generation.

## Current Status
- **Test Failures**: Reduced from 85+ to 71 failures
- **Successfully Converted**: bazel.py, pytest.py
- **Core Issues Fixed**: subset command imports, context passing, function signature preservation

## Remaining High-Priority Tasks

### 1. Fix Data Format Issues (Priority: Medium)
**Status**: Pending  
**Issue**: Many test failures are caused by data format mismatches (`group: ''` vs `group: None`)

**Files to investigate**:
- `launchable/commands/record/tests.py`
- Test data processing in various test runners
- JSON serialization/deserialization logic

**Expected Impact**: Could resolve 20-30 remaining test failures

### 2. Convert High-Priority Test Runners (Priority: Medium)
**Status**: Pending  
**Approach**: Use the proven static conversion pattern from bazel.py and pytest.py

**Priority test runners to convert**:
1. **maven.py** - Java build tool, commonly used
2. **gradle.py** - Java build tool, commonly used  
3. **jest.py** - JavaScript testing framework
4. **cypress.py** - End-to-end testing
5. **junit.py** - Java unit testing

**Conversion Pattern**:
```python
# Before (Click)
@click.option('--option-name', help="Help text")
def function(client, option_name):
    pass

# After (Typer)
def function(
    client,
    option_name: Annotated[Type, typer.Option(
        "--option-name",
        help="Help text"
    )] = default_value,
):
    pass
```

### 3. Complete Remaining Test Runner Conversions (Priority: Low)
**Status**: Pending  
**Count**: 15+ additional test runners

**Remaining test runners**:
- androidjunit.py
- ant.py  
- azuredevops.py
- behave.py
- bitscan.py
- cocoapods.py
- cucumber.py
- dotnet.py
- fastlane.py
- go_test.py
- minitest.py
- nunit.py
- rspec.py
- robot.py
- sbt.py
- swift.py
- unity.py
- file.py

### 4. Custom Type Validators (Priority: Low)
**Status**: Pending  
**Issue**: Click custom types need Typer equivalents

**Files to update**:
- `launchable/utils/click.py` - Contains PercentageType, DurationType
- `launchable/utils/typer_types.py` - Add Typer validators

**Required validators**:
- PercentageType → validate_percentage function
- DurationType → validate_duration function  
- KeyValueType → validate_key_value function

### 5. Error Handling Updates (Priority: Low)  
**Status**: Pending
**Issue**: Replace `click.ClickException` with `typer.BadParameter`

**Pattern**:
```python
# Before
raise click.ClickException("Error message")

# After  
raise typer.BadParameter("Error message")
```

## Detailed Conversion Instructions

### Static Conversion Process
1. **Analyze function signature**: Identify Click decorators and their parameters
2. **Convert decorators to annotations**: Transform @click.option/@click.argument to Annotated types
3. **Update error handling**: Replace Click exceptions with Typer equivalents
4. **Test conversion**: Verify the converted test runner works correctly

### Example Complete Conversion

**Before (Click)**:
```python
@click.argument('files', nargs=-1, required=True)
@click.option('--json', 'json_report', is_flag=True, help='use JSON reports')
@click.option('--output', help='output file')
def record_tests(client, files, json_report, output):
    if not files:
        raise click.ClickException("No files provided")
    # Implementation
```

**After (Typer)**:
```python
def record_tests(
    client,
    files: Annotated[List[str], typer.Argument(help="Test report files")],
    json_report: Annotated[bool, typer.Option(
        "--json", 
        help="use JSON reports"
    )] = False,
    output: Annotated[Optional[str], typer.Option(
        "--output",
        help="output file"
    )] = None,
):
    if not files:
        raise typer.BadParameter("No files provided")
    # Implementation  
```

## Testing Strategy

### Regression Testing
1. **Run specific test runners**: `uv run poe test tests/test_runners/test_<runner>.py`
2. **Check CLI functionality**: Test actual CLI commands with converted runners
3. **Verify API calls**: Ensure backend communication remains unchanged

### Success Criteria
- All test failures resolved (target: 0 failures)
- All CLI commands functional with converted test runners
- No regression in existing functionality
- Consistent error handling across all test runners

## Current Architecture Notes

### Function Signature Preservation
The wrapper function in `launchable/test_runners/launchable.py` preserves original function signatures:

```python
# Get the original function signature (excluding 'client' parameter)
sig = inspect.signature(f)
params = list(sig.parameters.values())[1:]  # Skip 'client' parameter

# Copy parameter annotations from original function (excluding client)
new_params = [inspect.Parameter('ctx', inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=typer.Context)]
new_params.extend(params)
typer_wrapper.__signature__ = sig.replace(parameters=new_params)
```

### Test Runner Registration
Test runners are automatically registered via the decorator system:
- `@launchable.subset` - registers subset commands
- `@launchable.record.tests` - registers record test commands  
- `@launchable.split_subset` - registers split subset commands

## Next Steps

1. **Immediate**: Address data format issues to reduce test failures
2. **Short-term**: Convert high-priority test runners (maven, gradle, jest, cypress, junit)
3. **Medium-term**: Complete conversion of remaining test runners
4. **Long-term**: Clean up legacy Click code and documentation

## Success Metrics
- **Current**: 71 test failures
- **Target**: 0 test failures
- **Converted runners**: 2/20+ (bazel, pytest)
- **Target**: 20+ runners converted
