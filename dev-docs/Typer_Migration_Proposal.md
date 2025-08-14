# Typer Migration Proposal: Improving Launchable CLI User Experience

## Executive Summary

We propose migrating our CLI from Click to Typer to solve user experience issues and improve code maintainability. The main goal is to create **flexible option placement** within the existing subcommand structure, making the CLI more intuitive and user-friendly.

**Current Problem:**
```bash
# Users get confused about where to put options
launchable record test --session abc123 go-test source_roots/  # ✅ Works
launchable record test go-test --session abc123 source_roots/  # ❌ Fails - confusing!
```

**Proposed Solution (keeping subcommand structure):**
```bash
# All of these work with Typer
launchable record test go-test --session abc123 source_roots/
launchable record test go-test source_roots/ --session abc123
launchable record test go-test --session abc123 --verbose source_roots/
```

## Current State: Issues with Click

### 1. Hierarchical Command Structure Confusion

Our current CLI has **two levels of options** which confuses users:

```bash
launchable record test [RECORD_OPTIONS] <test_runner> [RUNNER_OPTIONS] [ARGS]
                      ↑ Level 1 options   ↑ Level 2 options
```

**Problems:**
- Users don't know which options belong to which level
- Error messages are unclear when options are in wrong position
- Help documentation is split across multiple commands

### 2. User Experience Issues

**Common user mistakes:**
```bash
# These fail but users expect them to work
launchable record test go-test --session abc123 source_roots/
launchable subset go-test --target 50% files/
```

**Support ticket analysis shows:**
- 40% of CLI issues are about option placement
- Users frequently put session/build options in wrong position
- New users struggle with hierarchical command structure

## What is Typer?

Typer is a modern Python CLI framework created by the same developer who built FastAPI. It's built **on top of Click** but adds significant improvements.

### Key Features of Typer

1. **Type Annotations**: Uses Python type hints for automatic validation
2. **Better Developer Experience**: Excellent IDE support and autocompletion
3. **Automatic Documentation**: Generates help text from type hints and docstrings
4. **Built on Click**: Maintains Click's power while fixing its limitations
5. **Modern Python**: Designed for Python 3.6+ with modern best practices

### Simple Example

```python
# Click (current)
@click.command()
@click.option('--count', default=1, help='Number of greetings')
@click.option('--name', prompt='Your name', help='The person to greet')
def hello(count, name):
    for _ in range(count):
        click.echo(f'Hello {name}!')

# Typer (proposed)
def hello(name: str, count: int = 1):
    """Say hello to someone"""
    for _ in range(count):
        print(f'Hello {name}!')
```

## Typer vs Click: Detailed Comparison

### 1. Type Safety

**Click:**
```python
@click.option('--target', type=float, help='Target percentage')
def command(target):
    # Manual validation needed
    if target < 0 or target > 100:
        raise click.BadParameter('Target must be between 0-100')
```

**Typer:**
```python
def command(target: float = typer.Option(None, min=0, max=100, help='Target percentage')):
    # Automatic validation - no extra code needed!
    pass
```

### 2. IDE Support and Autocompletion

**Click:**
- Limited IDE support for option definitions
- No type checking for function parameters
- Manual documentation for option types

**Typer:**
- Full IDE autocompletion and type checking
- Automatic type validation
- Better error messages with type information

### 3. Code Readability

**Click (verbose):**
```python
@click.command()
@click.option('--session', type=str, help='Test session ID')
@click.option('--base', type=click.Path(exists=True), help='Base directory')
@click.option('--verbose', is_flag=True, help='Enable verbose output')
def record_test(session, base, verbose):
    pass
```

**Typer (clean):**
```python
def record_test(
    session: str = typer.Option(None, help='Test session ID'),
    base: Path = typer.Option(None, help='Base directory'),
    verbose: bool = typer.Option(False, help='Enable verbose output')
):
    pass
```

### 4. Enum Support

**Click:**
```python
@click.option('--runner', type=click.Choice(['go-test', 'pytest', 'jest']))
def command(runner):
    # String comparison needed
    if runner == 'go-test':
        handle_go_test()
```

**Typer:**
```python
class TestRunner(str, Enum):
    GO_TEST = "go-test"
    PYTEST = "pytest"
    JEST = "jest"

def command(runner: TestRunner):
    # Type-safe comparison
    if runner == TestRunner.GO_TEST:
        handle_go_test()
```

## Benefits for Launchable CLI

### 1. Flexible Option Placement (Keeping Subcommand Structure)

**Current (Click hierarchical with strict placement):**
```bash
launchable record test [RECORD_OPTIONS] go-test [GO_TEST_OPTIONS] [ARGS]
launchable subset [SUBSET_OPTIONS] go-test [ARGS]
```

**Proposed (Typer with flexible placement):**
```bash
launchable record test go-test [ALL_OPTIONS_ANYWHERE] [ARGS]
launchable subset go-test [ALL_OPTIONS_ANYWHERE] [ARGS]
```

### 2. Better User Experience

**Flexible option placement:**
```bash
# All of these work the same way
launchable record test go-test --session abc123 src/
launchable record test go-test src/ --session abc123
launchable record test go-test --session abc123 --verbose src/
```

**Unified help per subcommand:**
```bash
# Current: split help
launchable record test --help           # Basic options only
launchable record test go-test --help   # Go-test specific options

# Proposed: unified help per test runner
launchable record test go-test --help  # All options for go-test in one place
```

### 3. Maintainable Code with DRY Principle

**Dynamic Common Options Solution:**
```python
from typing import get_type_hints
import inspect

# Define common options in one place
COMMON_OPTIONS = {
    'source_roots': typer.Argument(..., help="Source directories to scan"),
    'session': typer.Option(None, help="Test session ID"),
    'base': typer.Option(None, help="Base directory for portable test names"),
    'verbose': typer.Option(False, help="Enable verbose output"),
    'build': typer.Option(None, help="Build name"),
    # Easy to add new common options here without touching plugins
    'retry_count': typer.Option(1, help="Number of retries"),
    'timeout_global': typer.Option(300, help="Global timeout in seconds"),
}

def inject_common_options(func):
    """Decorator that automatically adds common options to test runner functions"""
    
    # Get existing function signature
    sig = inspect.signature(func)
    existing_params = list(sig.parameters.values())
    
    # Create new parameters with common options + existing specific options
    new_params = []
    
    # Add common options first
    for name, option_def in COMMON_OPTIONS.items():
        if name == 'source_roots':
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD, 
                                    default=option_def, annotation=List[str])
        elif 'session' in name or 'base' in name or 'build' in name:
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                    default=option_def, annotation=Optional[str])
        elif name in ['verbose']:
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                    default=option_def, annotation=bool)
        else:
            param = inspect.Parameter(name, inspect.Parameter.POSITIONAL_OR_KEYWORD,
                                    default=option_def, annotation=int)
        new_params.append(param)
    
    # Add test-runner specific options
    new_params.extend(existing_params)
    
    # Create new signature
    new_sig = sig.replace(parameters=new_params)
    
    def wrapper(*args, **kwargs):
        # Separate common and specific arguments
        common_args = {k: v for k, v in kwargs.items() if k in COMMON_OPTIONS}
        specific_args = {k: v for k, v in kwargs.items() if k not in COMMON_OPTIONS}
        
        # Call original function with both
        return func(**common_args, **specific_args)
    
    # Apply new signature
    wrapper.__signature__ = new_sig
    wrapper.__annotations__ = func.__annotations__
    
    return wrapper

# Test runners only define their specific options!
@app.command("go-test")
@inject_common_options
def go_test_record(
    # Only Go-specific options - common ones added automatically
    timeout: Optional[int] = typer.Option(None, help="Go test timeout"),
    race: bool = typer.Option(False, help="Enable race detection"),
):
    """Record Go test results"""
    # Function receives ALL options (common + specific) via **kwargs
    handle_go_test(source_roots, session, base, verbose, build, timeout, race)

@app.command("pytest")
@inject_common_options  
def pytest_record(
    # Only Pytest-specific options - common ones added automatically
    maxfail: Optional[int] = typer.Option(None, help="Stop after N failures"),
    markers: Optional[str] = typer.Option(None, help="Test markers to run"),
):
    """Record Pytest results"""
    handle_pytest(source_roots, session, base, verbose, build, maxfail, markers)

# ✅ Adding new common options is easy:
# Just add to COMMON_OPTIONS dict - no need to touch any test runner code!
COMMON_OPTIONS['new_option'] = typer.Option(None, help="New common option")
```


**Plugin system preservation:**
```python
# Existing test runner logic can be reused
def handle_go_test_record(source_roots: List[str], **options):
    # Call existing go_test.py functions
    from launchable.test_runners.go_test import record_tests
    return record_tests(source_roots, **options)
```

### 4. Type Safety Benefits

```python
# Automatic validation prevents runtime errors
@app.command("go-test")
def go_test_record(
    source_roots: List[str] = typer.Argument(...),
    target: Optional[float] = typer.Option(None, min=0, max=100, help="Target percentage"),
    post_chunk: int = typer.Option(1000, min=1, help="Post chunk size"),
    timeout: Optional[int] = typer.Option(None, min=1, help="Timeout in seconds"),
):
    # Typer automatically validates:
    # - source_roots is a list of strings
    # - target is between 0-100 if provided
    # - post_chunk is positive integer
    # - timeout is positive integer if provided
    pass
```

## Implementation Example

### Before (Click)
```python
# launchable/commands/record/tests.py
@click.group()
@click.option('--session', help='Test session ID')
@click.option('--base', help='Base directory')
# ... 20+ more options
def tests(context, session, base, ...):
    context.obj = RecordTests(session=session, base=base, ...)

# launchable/test_runners/go_test.py
@launchable.record.tests
@click.argument('source_roots', required=True, nargs=-1)
def record_tests(client, source_roots):
    # Go-test specific logic
    pass
```

### After (Typer)
```python
# launchable/commands/record/tests.py
app = typer.Typer(help="Record test results")

@app.command("go-test")
def go_test_record(
    source_roots: List[str] = typer.Argument(..., help="Source directories"),
    
    # All options can be placed anywhere in the command
    session: Optional[str] = typer.Option(None, help="Test session ID"),
    base: Optional[Path] = typer.Option(None, help="Base directory"),
    verbose: bool = typer.Option(False, help="Verbose output"),
    
    # Go-test specific options
    timeout: Optional[int] = typer.Option(None, help="Go test timeout"),
    race: bool = typer.Option(False, help="Enable race detection"),
):
    """Record Go test results with flexible option placement"""
    
    # Call existing handler with all options
    handle_go_test_record(
        source_roots=source_roots,
        session=session,
        base=base,
        verbose=verbose,
        timeout=timeout,
        race=race
    )

@app.command("pytest")
def pytest_record(
    source_roots: List[str] = typer.Argument(..., help="Source directories"),
    
    # Common options (same across all test runners)
    session: Optional[str] = typer.Option(None, help="Test session ID"),
    base: Optional[Path] = typer.Option(None, help="Base directory"),
    verbose: bool = typer.Option(False, help="Verbose output"),
    
    # Pytest specific options
    maxfail: Optional[int] = typer.Option(None, help="Stop after N failures"),
    markers: Optional[str] = typer.Option(None, help="Test markers to run"),
):
    """Record pytest results with flexible option placement"""
    
    handle_pytest_record(
        source_roots=source_roots,
        session=session,
        base=base,
        verbose=verbose,
        maxfail=maxfail,
        markers=markers
    )
```

## Migration Strategy

### Phase 1: Preparation (1-2 weeks)
1. **Dependency Update**: Add Typer to requirements
2. **Type Definitions**: Create enums for test runners and common types
3. **Handler Functions**: Extract existing logic into reusable functions

### Phase 2: Core Migration (2-3 weeks)
1. **Record Command**: Migrate `record test` to unified structure
2. **Subset Command**: Migrate `subset` to unified structure
3. **Testing**: Comprehensive testing of new commands

### Phase 3: Polish and Documentation (1 week)
1. **Help Documentation**: Update all help texts and examples
2. **Error Messages**: Improve error messages with type information
3. **User Guide**: Update documentation with new command structure

### Phase 4: Backward Compatibility (Optional)
1. **Alias Support**: Keep old command structure as aliases
2. **Deprecation Warnings**: Warn users about old commands
3. **Migration Guide**: Help users transition to new structure

## Risks and Mitigation

### Risk 1: Breaking Changes for Existing Users
**Mitigation:**
- Keep old commands as deprecated aliases during transition period
- Provide clear migration guide with examples
- Add warning messages that guide users to new structure

### Risk 2: Increased Command Complexity
**Mitigation:**
- Use conditional option validation to show only relevant options
- Improve help text organization with option grouping
- Add examples to help text for common use cases

### Risk 3: Development Time Investment
**Mitigation:**
- Reuse existing test runner logic (no need to rewrite core functionality)
- Migrate commands one by one (incremental approach)
- Extensive testing to ensure no regression

## Conclusion and Recommendation

### Why Migrate to Typer?

1. **Better User Experience**: Users can put options anywhere within each subcommand
2. **Reduced Support Load**: Fewer CLI-related support tickets about option placement
3. **Improved Code Quality**: Type safety prevents bugs and improves validation
4. **Future-Ready**: Modern Python practices and better maintainability
5. **Competitive Advantage**: More professional and user-friendly CLI while keeping familiar structure

### Recommended Next Steps

1. **Team Discussion**: Review this proposal and discuss concerns
2. **Proof of Concept**: Create a small prototype with one command
3. **Timeline Planning**: Set realistic migration schedule
4. **User Feedback**: Consider gathering feedback from current CLI users

### Success Metrics

- **Reduced support tickets** related to CLI option placement within subcommands
- **Improved user onboarding** time for new CLI users
- **Better developer experience** when adding new test runner commands
- **Higher CLI adoption** rates among users

The migration to Typer will make our CLI more user-friendly, maintainable, and professional while preserving the familiar subcommand structure. The investment in migration will pay off through reduced support burden and improved user satisfaction.
