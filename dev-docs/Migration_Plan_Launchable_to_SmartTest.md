# Migration Plan: Launchable CLI to SmartTest CLI

## Difference Analysis Results

### Major Changes

#### 1. Branding Changes
- "Launchable CLI v1" → "SmartTest CLI v1"

#### 2. record build Command
- **Options to be removed:**
  - `--scrub-pii` option
  - `--link` option
- **Options to be modified:**
  - `--branch` option becomes required (required: no → yes)
- **New options to be added:**
  - `--repository` option (required: no)

#### 3. record commit Command
- **Options to be removed:**
  - `--executable` option (already deprecated)
  - `--scrub-pii` option (already deprecated)

#### 4. record session Command
- **Options to become required:**
  - `--build` option (required: no → yes)
  - `--test-suite` option (required: no → yes)
- **Option name changes:**
  - `--session-name` → `--name` (and becomes required)
- **Options to be removed:**
  - `--lineage` option

#### 5. record tests Command
- **Options to be removed:**
  - `--build` option
  - `--session-name` option
  - `--lineage` option
  - `--test-suite` option
  - `--link` option
  - `--timestamp` option
- **Options to be modified:**
  - `--session` description change:
    - Current: "Test session ID"
    - New: "Test session name specified in record session"
  - `--session` becomes required (required: no → yes)

#### 6. subset Command
- **Options to be removed:**
  - `--build` option
  - `--session-name` option
  - `--lineage` option
  - `--test-suite` option
  - `--link` option
- **Options to be modified:**
  - `--session` description change:
    - Current: "Test session ID"
    - New: "Test session name specified in record session"
  - `--session` becomes required (required: no → yes)
- **split-subset functionality integration:**
  - Add `--bin` option
  - Add `--same-bin` option
  - Add `--split-by-groups` option
  - Add `--split-by-groups-with-rest` option
  - Add `--split-by-groups-output-dir` option
  - Add `--output-exclusion-rules` option (duplicate)

#### 7. record attachment Command
- **Options to be modified:**
  - `--session` description change:
    - Current: "Test session ID"
    - New: "Test session name specified in record session"
  - `--session` becomes required (required: no → yes)

#### 8. Command Removal
- **Commands to be completely removed:**
  - `split-subset` command (functionality integrated into subset command)
  - `inspect tests` command

## Migration Steps

### Phase 1: Session Management Architecture Changes
**Objective**: Change session identifiers from ID-based to name-based

**Work Items:**
1. **Session identifier changes**
   - Modify session processing logic in `launchable/utils/session.py`
   - Change from session ID → session name references
   - Update database/API session search logic

2. **Update record session command**
   - Update `launchable/commands/record/session.py`
   - Change argument name from `--session-name` → `--name`
   - Make `--build` and `--test-suite` required parameters
   - Remove `--lineage` option

3. **Update related tests**
   - Update session-related test cases
   - Update mock data

**Impact Scope:** High
**Estimated Effort:** 3-5 days

### Phase 2: Build Management Enhancement
**Objective**: Strengthen branch and repository management

**Work Items:**
1. **Update record build command**
   - Update `launchable/commands/record/build.py`
   - Make `--branch` option required
   - Add and implement `--repository` option
   - Remove `--scrub-pii` and `--link` options

2. **Clean up record commit command**
   - Update `launchable/commands/record/commit.py`
   - Completely remove deprecated options

**Impact Scope:** Medium
**Estimated Effort:** 2-3 days

### Phase 3: Command Integration and Test-related Changes
**Objective**: Integrate split-subset functionality into subset and simplify tests command

**Work Items:**
1. **Extend subset command**
   - Update `launchable/commands/subset.py`
   - Integrate all split-subset functionality
   - Implement new option groups
   - Convert session references to name-based

2. **Simplify record tests command**
   - Update `launchable/commands/record/tests.py`
   - Remove unnecessary options
   - Convert session references to name-based and make required

3. **Update record attachment command**
   - Update `launchable/commands/record/attachment.py`
   - Convert session references to name-based and make required

**Impact Scope:** High
**Estimated Effort:** 4-6 days

### Phase 4: Command Removal and Final Cleanup
**Objective**: Remove unnecessary commands and ensure overall consistency

**Work Items:**
1. **Command removal**
   - Delete `launchable/commands/split_subset.py`
   - Delete `launchable/commands/inspect/tests.py`
   - Remove references from main application

2. **Final consistency check**
   - Update all help texts
   - Update error messages
   - Apply branding changes

3. **Comprehensive test suite update**
   - Remove tests for deleted commands
   - Update tests for changed options
   - Add tests for integrated functionality

**Impact Scope:** Medium
**Estimated Effort:** 2-4 days

### Phase 5: Documentation and Release Preparation
**Objective**: Update documentation and create migration guide

**Work Items:**
1. **Documentation updates**
   - Update README.md
   - Update CLAUDE.md
   - Comprehensive review of command help

2. **Create migration guide**
   - Migration guide for existing users
   - Detailed explanation of breaking changes
   - Usage instructions for new features

3. **Create release notes**
   - Organize changes
   - Document compatibility information

**Impact Scope:** Low
**Estimated Effort:** 1-2 days

## Risk Assessment and Mitigation

### High Risk Items
1. **Session management changes**
   - **Risk**: Disruption of existing workflows
   - **Mitigation**: Gradual migration, temporary backward compatibility maintenance

2. **Addition of required parameters**
   - **Risk**: Existing scripts stop working
   - **Mitigation**: Clear migration guide, version management

### Medium Risk Items
1. **Command integration**
   - **Risk**: Missing functionality or inconsistencies
   - **Mitigation**: Create detailed test cases, feature comparison table

2. **Option removal**
   - **Risk**: Existing user confusion
   - **Mitigation**: Deprecation notices, provide alternative methods

## Success Criteria

1. **Feature completeness**: All existing features available in new format
2. **Test coverage**: Maintain existing test coverage rate
3. **Performance**: Maintain existing performance metrics
4. **Usability**: Improve usability of new interface

## Total Estimated Effort
- **Development**: 12-20 days
- **Testing**: 5-8 days
- **Documentation**: 2-3 days
- **Total**: 19-31 days

## Recommended Implementation Order
1. Phase 1 (Session Management) - Implement first due to highest impact
2. Phase 2 (Build Management) - Implement next as it integrates with session management
3. Phase 3 (Command Integration) - Main functionality integration
4. Phase 4 (Cleanup) - Remove unnecessary features
5. Phase 5 (Documentation) - Final preparation work
