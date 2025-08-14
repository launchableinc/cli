# SmartTest CLI Migration - Remaining Tasks

## Overview
This document outlines the remaining tasks to complete the migration from Launchable CLI v1 to SmartTest CLI v1, based on analysis of the specification documents and current codebase implementation.

## Migration Status Summary

### ✅ Completed
- Click to Typer framework migration (100% complete)
- Basic command structure and global options
- Most core commands implemented with Typer
- Test runner plugin system functional
- Session management partially updated (--session is now required in record session)
- Made `--test-suite` required in `record session` command
- Removed `inspect tests` command (but kept `inspect subset` command)
- Updated `record build` command options (removed --scrub-pii, --link; made --branch required; added --repository)
- Updated `record tests` command options (removed --link, --lineage, --test-suite, --timestamp)
- Updated `subset` command options (removed --link, --lineage, --test-suite)
- Updated `record attachment` command options
- Removed `--lineage` option from `record session` command
- Restored `inspect subset` command (accidentally removed)
### ❌ Major Tasks Remaining

## 1. Remaining Tasks

### 1.1 Remaining `record session` Command Updates
- **Make Required**:
  - `--build` (currently optional) - Note: Not implemented due to session lookup design constraints
- **✅ Remove Option**:
  - ~~`--lineage` (still present, needs to be removed)~~ - ✅ COMPLETED

## 3. Session Management Architecture Changes

### 3.1 Session Identifier Migration
**Priority: HIGH**
- **Current**: Mixed use of session IDs and names
- **Target**: Consistent use of session names as identifiers
- **Files to Update**:
  - `smart_tests/utils/session.py`
  - All commands that reference sessions
  - API client code
- **Impact**: Potentially breaking change for API integration

## 4. Documentation Updates

### 4.1 Update CLAUDE.md
- Reflect all command changes
- Update development commands if needed

### 4.2 Migration Guide
- Create comprehensive migration guide for users
- Document all breaking changes
- Provide examples of old vs new command usage

## 5. Testing Requirements

### 5.1 Update Existing Tests
- Modify tests for changed command options
- Remove tests for deleted commands/options
- Add tests for new required parameters

### 5.2 Add New Tests
- Tests for session name-based identification
- Tests for new required parameters

## Implementation Notes

### Session Lookup Design Issue
The original migration plan called for removing `--build` from various commands, but the API design requires a build name to look up sessions because session names are only unique within a build context. 

As a workaround, all commands that removed `--build` now default to using the "nameless" build (equivalent to `--no-build` behavior) when looking up sessions by name. This maintains backward compatibility while following the migration requirements as closely as possible.

### Completed Tasks Summary
1. ✅ Made `--test-suite` required in `record session`
2. ✅ Removed `--lineage` option from `record session` command
3. ✅ Updated `record build` command (removed options, made --branch required, added --repository)
4. ✅ Updated `record tests` command (removed link/lineage/test-suite/timestamp options)
5. ✅ Updated `subset` command (removed link/lineage/test-suite options)
6. ✅ Updated `record attachment` command
7. ✅ Restored `inspect subset` command (accidentally removed)
8. ✅ All tests updated and passing

## Risk Assessment

### High Risk
- **Breaking Changes**: Many options becoming required will break existing scripts
- **Session Management**: Switching from IDs to names may affect existing integrations
- **Mitigation**: Consider adding deprecation warnings before removing options

### Medium Risk
- **Test Coverage**: Ensuring all edge cases are covered
- **Mitigation**: Extensive testing and gradual rollout

## Success Criteria

1. All commands match SmartTest CLI v1 specification exactly
2. No regression in existing functionality
3. All tests pass with >90% coverage
4. Clear migration documentation available
5. Deprecation warnings for breaking changes (if implementing gradual migration)

## Estimated Timeline

- **Total Development**: 2-3 weeks
- **Testing & QA**: 1 week
- **Documentation**: 2-3 days
- **Total**: ~4 weeks

## Next Steps

1. Review and approve this migration plan
2. Decide on breaking change strategy (immediate vs gradual with deprecation)
3. Begin implementation starting with Phase 1 critical features
4. Set up tracking for migration progress
