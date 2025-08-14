# Smart Tests CLI Backport Plan

## Executive Summary

This document outlines the comprehensive plan to backport changes from the `main` branch to the `smart-tests` branch. The Smart Tests CLI is the next-generation CLI under development, and we need to incorporate the latest fixes and features from the current generation.

## Branch Analysis Results

### Current Status
- **Source Branch**: `main` (current generation CLI with `launchable` package)
- **Target Branch**: `smart-tests` (next-generation CLI with `smart_tests` package)
- **Common Ancestor**: `9971c58e` (last common commit)
- **Architecture Differences**: Click → Typer, pipenv → uv, package restructuring

### Commits to Backport: 28 Merge Commits
Analysis shows 28 Pull Request merge commits from `main` branch that need to be backported to `smart-tests` branch.

## Merge Commits to Backport (Chronological Order)

### Phase 1: Foundation and Core Fixes
1. **536cd008** - `#1046 fail-fast-mode`
   - **Priority**: Critical
   - **Description**: Introduces comprehensive fail-fast mode functionality
   - **Impact**: Core CLI behavior enhancement with validation utilities
   - **Files**: Command validators, helper utilities, multiple test runners

2. **e40f89e5** - `#1060 tagpr-from-v1.105.1`
   - **Priority**: Low
   - **Description**: Release preparation for v1.105.1

3. **3df625be** - `#1072 fix-pytest`
   - **Priority**: High
   - **Description**: Enhanced pytest JSON report parsing with longrepr handling
   - **Impact**: Test result parsing improvements
   - **Files**: pytest parser, unit tests

4. **3e927707** - `#1074 tagpr-from-v1.106.0`
   - **Priority**: Low
   - **Description**: Release preparation

5. **b30d5a59** - `#1071 AIENG-183`
   - **Priority**: High
   - **Description**: Optional file content collection mode
   - **Impact**: Git commit processing, Java JAR updates
   - **Files**: Java components, commit collector

### Phase 2: Quality and Infrastructure Updates
6. **cf9abbd9** - `#1076 tagpr-from-v1.106.1`
   - **Priority**: Low

7. **44bda06f** - `#1075 fix-install-git`
   - **Priority**: Medium
   - **Description**: Git installation fixes in Docker build
   - **Impact**: CI/CD pipeline reliability

8. **4644a6f0** - `#1079 support-deps`
   - **Priority**: High
   - **Description**: Enhanced pytest JSON parsing for user properties and dependencies
   - **Impact**: Test metadata collection
   - **Files**: pytest JSON report parser

9. **27b4392d** - `#1078 tagpr-from-v1.107.0`
   - **Priority**: Low

10. **c697332d** - `#1077 AIENG-180`
    - **Priority**: Medium
    - **Description**: Improved Java version error handling
    - **Impact**: Java compatibility checks

### Phase 3: Test Framework Improvements
11. **d348ef88** - `#1080 tagpr-from-v1.107.1`
    - **Priority**: Low

12. **6849a8f3** - `#1083 rename-field-name`
    - **Priority**: High
    - **Description**: Rename 'properties' to 'markers' in pytest parser for consistency
    - **Impact**: Test result data structure standardization

13. **a679d873** - `#1085 tagpr-from-v1.107.2`
    - **Priority**: Low

14. **f9755c1f** - `#1084 AIENG-202`
    - **Priority**: Medium
    - **Description**: Display warning when total test duration is 0
    - **Impact**: User experience enhancement

15. **ab02c6ff** - `#1087 tagpr-from-v1.107.3`
    - **Priority**: Low

16. **69957832** - `#1081 subset-file-auto-collection`
    - **Priority**: Critical
    - **Description**: Auto test file collection for PTS v2 workspaces
    - **Impact**: Major subset functionality enhancement
    - **Files**: Core subset command (280+ lines changed), client utilities

### Phase 4: Session Management and Validation
17. **ee4344a9** - `#1090 tagpr-from-v1.107.4`
    - **Priority**: Low

18. **4bcb9e24** - `#1091 AIENG-204`
    - **Priority**: High
    - **Description**: Session flag format validation in subset command
    - **Impact**: Session management improvements
    - **Files**: Helper functions, session utilities, subset command

19. **837737a4** - `#1093 tagpr-from-v1.108.0`
    - **Priority**: Low

20. **561c0b2c** - `#1086 deprecated-pkg-resources`
    - **Priority**: High
    - **Description**: Replace deprecated pkg_resources with importlib_metadata
    - **Impact**: Python 3.13+ compatibility and modernization
    - **Files**: Version utilities, setup configuration

### Phase 5: Advanced Features and Java Components
21. **094b548e** - `#1092 AIENG-182`
    - **Priority**: Critical
    - **Description**: Progress reporting for file transfer in Java components
    - **Impact**: Major Java JAR updates, user experience
    - **Files**: Multiple Java source files, new progress reporting classes

22. **fbd26c6d** - `#1095 scrub-pii-fixup`
    - **Priority**: High
    - **Description**: Follow-up fix for PII scrubbing functionality
    - **Impact**: Security/privacy improvements
    - **Files**: commit record command

23. **827f28c3** - `#1094 tagpr-from-v1.108.1`
    - **Priority**: Low

24. **ef481252** - `#1044 renovate/actions-attest-build-provenance-2.x`
    - **Priority**: Low
    - **Description**: Update GitHub Actions build provenance to v2.4.0
    - **Impact**: CI/CD security improvements

### Phase 6: Latest Fixes and Improvements
25. **3dd447d4** - `#1098 fix-send-file-name`
    - **Priority**: High
    - **Description**: Send only filename instead of repo + filename
    - **Impact**: File transmission optimization
    - **Files**: Java FileChunkStreamer components

26. **da859e66** - `#1096 tagpr-from-v1.109.0`
    - **Priority**: Low

27. **590aae07** - `#1099 error-reporting-problem`
    - **Priority**: Medium
    - **Description**: Fix error reporting issue in Java component
    - **Impact**: Debugging improvements

28. **3181a42e** - `#1101 rename-to-cb-oss`
    - **Priority**: Medium
    - **Description**: Update GitHub repository URLs to cloudbees-oss
    - **Impact**: Repository migration updates
    - **Files**: GitHub workflows, helper functions

### Phase 7: Final Updates
29. **22fc4c47** - `#1102 LCHIB-641`
    - **Priority**: High
    - **Description**: Windows error handling for missing '%' character
    - **Impact**: Cross-platform compatibility
    - **Files**: Click utilities, error handling

30. **e1ff1d31** - `#1106 report-endpoint`
    - **Priority**: High
    - **Description**: Report the API endpoint being used
    - **Impact**: Debugging and transparency improvements
    - **Files**: verify command, launchable client

## Backport Strategy

### Execution Approach
We will cherry-pick merge commits in **chronological order** (oldest first) to maintain logical development progression. Each merge commit represents a complete, tested Pull Request.

### Priority-Based Execution Order

#### Critical Priority (Execute First)
- **536cd008** - Fail-fast mode functionality
- **69957832** - PTS v2 subset auto-collection  
- **094b548e** - Java progress reporting improvements

#### High Priority (Execute Second) 
- **3df625be** - Pytest JSON parsing enhancements
- **b30d5a59** - Java file content collection mode
- **4644a6f0** - Pytest user properties support
- **6849a8f3** - Pytest field name standardization
- **4bcb9e24** - Session flag validation
- **561c0b2c** - pkg_resources → importlib_metadata migration
- **fbd26c6d** - PII scrubbing security fix
- **3dd447d4** - Java filename transmission fix
- **22fc4c47** - Windows error handling
- **e1ff1d31** - API endpoint reporting

#### Medium Priority (Execute Third)
- **44bda06f** - Git installation CI fixes
- **c697332d** - Java version error handling
- **f9755c1f** - Zero test duration warnings
- **590aae07** - Java error reporting fixes
- **3181a42e** - Repository URL updates

#### Low Priority (Execute Last)
- All release preparation commits (tagpr-*)
- **ef481252** - GitHub Actions dependency updates

## Implementation Approach

### Merge Commit Unit Execution Strategy

Execute cherry-pick **one merge commit at a time**, followed by complete testing before proceeding to the next commit:

```bash
# Switch to smart-tests branch
git checkout smart-tests

# Execute ONE merge commit at a time:
git cherry-pick -m 1 536cd008  # #1046 fail-fast-mode
# Resolve conflicts if any
# Run full test suite
uv run poe test && uv run poe lint && uv run poe type
# Only proceed to next commit after tests pass

git cherry-pick -m 1 e40f89e5  # #1060 tagpr-from-v1.105.1  
# Resolve conflicts, test, then continue...
```

### Manual Adaptation Required
Due to architectural differences between branches, each cherry-pick will require manual resolution:

#### 1. Package Structure Mapping
- **Import Updates**: `launchable.*` → `smart_tests.*`
- **Module Paths**: Update all internal imports to match Smart Tests structure
- **Entry Points**: Adapt setup.cfg/pyproject.toml entry points

#### 2. CLI Framework Translation  
- **Click → Typer**: Convert decorators and command structures
  ```python
  # From (Click):
  @click.command()
  @click.option('--option', help="Help text")
  
  # To (Typer):  
  @smart_tests.record  # or appropriate decorator
  def command(option: str = typer.Option(None, help="Help text"))
  ```
- **Error Handling**: Update Click-specific error patterns to Typer equivalents
- **Context Objects**: Adapt ctx.obj usage to Smart Tests context management

#### 3. File Structure Differences
- **Test Runners**: Map `launchable/test_runners/` to `smart_tests/test_runners/`
- **Commands**: Map `launchable/commands/` to `smart_tests/commands/`
- **Utilities**: Update utility imports and references

#### 4. Configuration Adaptations
- **Environment Variables**: Update LAUNCHABLE_* references where appropriate
- **Java Integration**: Ensure JAR path references work with Smart Tests structure
- **Plugin System**: Adapt plugin loading to Typer-based system

## Expected Conflicts and Resolution Strategy

### High Probability Conflicts
1. **Package Imports**: All `from launchable` imports need → `from smart_tests`
2. **CLI Decorators**: Click decorators need conversion to Typer equivalents
3. **Command Structure**: Different command registration and option handling
4. **JAR File Paths**: Java component references may need path updates
5. **Test File Structure**: Test imports and module references

### Resolution Patterns
```bash
# For each conflict during cherry-pick:
1. git status  # Check conflicted files
2. # Edit files to resolve conflicts:
   - Update package imports
   - Convert CLI decorators  
   - Fix file paths
3. git add <resolved_files>
4. git cherry-pick --continue
```

## Per-Merge-Commit Workflow

### Step-by-Step Process for Each Merge Commit

1. **Cherry-pick single merge commit**:
   ```bash
   git cherry-pick -m 1 <commit-hash>
   ```

2. **Resolve conflicts** (if any):
   ```bash
   git status  # Check conflicted files
   # Edit files to resolve conflicts
   git add <resolved_files>
   git cherry-pick --continue
   ```

3. **Complete testing before next commit**:
   ```bash
   # Required test suite - ALL must pass
   uv run poe test        # Run full test suite
   uv run poe lint        # Check code style  
   uv run poe type        # Type checking
   uv run poe build       # Verify build works
   
   # Basic CLI functionality verification
   uv run smart-tests verify
   uv run smart-tests subset --help
   uv run smart-tests record --help
   ```

4. **Only proceed to next merge commit after ALL tests pass**

5. **Document any significant adaptations made**

## Success Criteria (Per Merge Commit)

For **each merge commit**, the following must be satisfied before proceeding to the next:

- [ ] Cherry-pick completed successfully (conflicts resolved)
- [ ] **Test suite passes**: `uv run poe test` ✅
- [ ] **Linting passes**: `uv run poe lint` ✅
- [ ] **Type checking passes**: `uv run poe type` ✅  
- [ ] **Build process works**: `uv run poe build` ✅
- [ ] **CLI commands functional**: Basic verify/subset/record commands work
- [ ] **No regressions**: Existing Smart Tests functionality intact

## Overall Success Criteria

- [ ] All 28 merge commits successfully processed with per-commit validation
- [ ] Final comprehensive testing across all test runners
- [ ] Java component integration working
- [ ] Performance validation (no regressions)
- [ ] Documentation updated to reflect backported features

## Timeline (Per-Merge-Commit Approach)

### Estimated Time per Merge Commit:
- **Critical Priority** (3 commits): 4-6 hours each (complex conflicts, extensive testing)
- **High Priority** (10 commits): 2-3 hours each (moderate conflicts, thorough testing)  
- **Medium Priority** (5 commits): 1-2 hours each (minor conflicts, standard testing)
- **Low Priority** (10 commits): 30-60 minutes each (minimal conflicts, quick validation)

### Daily Breakdown:
- **Day 1**: Critical priority commits (3 commits) - 12-18 hours
- **Day 2-4**: High priority commits (10 commits) - 20-30 hours  
- **Day 5**: Medium priority commits (5 commits) - 5-10 hours
- **Day 6**: Low priority commits (10 commits) - 5-10 hours
- **Day 7**: Final validation and documentation

**Total Estimated Duration**: 1 week with per-commit validation ensuring quality at each step

## Rollback Strategy (Per-Merge-Commit)

Since we process one merge commit at a time with full validation, rollback is straightforward:

### During Cherry-Pick (if conflicts are too complex):
```bash
# Abort current cherry-pick
git cherry-pick --abort
# Document the problematic commit 
# Skip to next commit or address separately
```

### After Cherry-Pick (if tests fail):
```bash
# Reset to previous good state (before this commit)
git reset --hard HEAD~1
# Document the issue
# Re-attempt with different approach or skip temporarily
```

### Advantage of Per-Commit Approach:
- **Isolated failures**: Each commit is independently validated
- **Clean rollback points**: Always know the last working state
- **Progressive validation**: Issues caught immediately, not after multiple commits
- **Easier debugging**: Can isolate which specific change caused problems

## Post-Backport Actions

1. **Update Documentation**: Reflect new features in Smart Tests CLI docs
2. **Version Planning**: Determine version number for updated Smart Tests CLI
3. **Integration Testing**: Comprehensive testing with various test runners
4. **Performance Validation**: Ensure no performance regressions
