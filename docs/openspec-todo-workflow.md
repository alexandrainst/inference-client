# OpenSpec-Enhanced TODO Workflow Documentation

This document describes the enhanced TODO workflow patterns for AI assistants working in OpenSpec projects. It extends the base TODO system with spec-driven development practices.

## Overview

The OpenSpec-enhanced TODO workflow integrates structured change proposals with granular task tracking, ensuring that every implementation step is traceable to specific requirements and scenarios.

## Configuration Files

### Primary Configuration
- **File**: `.openspec-todo-config.yml`
- **Purpose**: Contains all workflow rules, templates, and validation requirements
- **Format**: YAML with structured data for programmatic access

### Supporting Files
- **Documentation**: `docs/openspec-todo-workflow.md` (this file)
- **Validation Scripts**: `scripts/validate-todo-workflow.sh`

## Enhanced TODO States

| State | Description | Usage Context |
|-------|-------------|---------------|
| `pending` | Task not yet started | Default state for new todos |
| `in_progress` | Currently being worked on | Only ONE at a time |
| `awaiting_approval` | Completed, waiting for confirmation | OpenSpec approval gates |
| `completed` | Finished and verified | After validation passes |

## OpenSpec Integration Workflow

### Phase 1: Context Gathering

Before creating any todos:

```bash
# Check for active changes
openspec list

# List existing capabilities  
openspec list --specs

# Read specific change details
openspec show <change-id>
```

### Phase 2: TODO Creation

Use change-ID-aware naming and spec references:

```bash
# Example: add-two-factor-auth change
todowrite([
  {
    id: "add-two-factor-auth-1",
    content: "Read proposal.md and design.md for add-two-factor-auth",
    status: "pending",
    priority: "high"
  },
  {
    id: "add-two-factor-auth-2", 
    content: "Create OTP database schema (tasks.md:1.1) - refs specs/auth/spec.md:3",
    status: "pending",
    priority: "medium"
  }
])
```

### Phase 3: Implementation with Approval Gates

For each todo in the change proposal:

1. **Mark as `in_progress`**
2. **Implement the task**
3. **Mark as `awaiting_approval`**
4. **Show results and ask for confirmation**
5. **Only then mark as `completed`**

### Phase 4: Validation and Completion

Before completing the entire change:

```bash
# Validate the change
openspec validate <change-id> --strict

# If validation passes, archive after deployment
openspec archive <change-id> --yes
```

## TODO Templates

### Template 1: New Feature Implementation
```json
{
  "id": "{change-id}-1",
  "content": "Read proposal.md and design.md for {change-id}",
  "status": "pending",
  "priority": "high"
}
```

### Template 2: Spec Requirement Implementation  
```json
{
  "id": "{change-id}-{number}",
  "content": "{Task description} (tasks.md:{item-number}) - refs specs/{capability}/spec.md:{line-number}",
  "status": "pending",
  "priority": "medium"
}
```

### Template 3: Validation Task
```json
{
  "id": "{change-id}-validate",
  "content": "Run openspec validate {change-id} --strict and fix any issues",
  "status": "pending",
  "priority": "high"
}
```

## Quality Checklists

### Before Creating Todos
- [ ] Checked `openspec list` for active changes
- [ ] Read `proposal.md` for the change
- [ ] Read `design.md` if it exists
- [ ] Reviewed `tasks.md` for implementation checklist
- [ ] Identified affected spec files

### Before Completing Each Todo
- [ ] Implementation matches spec requirements
- [ ] All scenarios in requirements are handled
- [ ] Code follows project patterns
- [ ] Tests pass (if applicable)
- [ ] `openspec validate` passes without errors

### Before Marking Change Complete
- [ ] All todos in `tasks.md` are completed
- [ ] `openspec validate {change-id> --strict` passes
- [ ] All approval gates cleared
- [ ] Ready for archiving

## Integration with Base TODO System

The enhanced workflow maintains all base TODO system principles with OpenSpec-specific priority overrides:

1. **Immediate Creation**: Create todos immediately when receiving non-trivial tasks
2. **Single In-Progress**: Only one todo marked `in_progress` at any time
3. **Approval-First Completion**: For OpenSpec changes, follow approval gates before marking `completed`
4. **Evidence Required**: Provide concrete evidence for all completions

### Priority System

When conflicts arise between OpenSpec workflow and system behaviors:

| Priority | Rule | Application |
|----------|------|-------------|
| 1 (Highest) | **OpenSpec Approval Gates** | Always ask for confirmation on OpenSpec changes |
| 2 | **System Reminders** | Ignore when OpenSpec approval workflow is active |
| 3 (Lowest) | **Base TODO Flow** | Default for non-OpenSpec tasks |

**AI Assistant Behavior**: The approval workflow takes absolute precedence over system continuation reminders. When working on OpenSpec changes, the assistant must: `in_progress` → implement → `awaiting_approval` → show results → wait for confirmation → `completed`.

## Examples

### Example 1: Simple Feature Addition

**Change**: `add-user-profile`

**Todos Created**:
```yaml
- id: "add-user-profile-1"
  content: "Read proposal.md and design.md for add-user-profile"
  status: "pending"
  priority: "high"
  
- id: "add-user-profile-2" 
  content: "Create user profile database schema (tasks.md:1.1) - refs specs/users/spec.md:3"
  status: "pending"
  priority: "medium"
  
- id: "add-user-profile-3"
  content: "Implement profile API endpoints (tasks.md:1.2) - refs specs/users/spec.md:4"
  status: "pending"
  priority: "medium"
  
- id: "add-user-profile-validate"
  content: "Run openspec validate add-user-profile --strict and fix any issues"
  status: "pending"
  priority: "high"
```

### Example 2: Multi-Capability Change

**Change**: `add-2fa-notify` (affects auth and notifications)

**Todos Created**:
```yaml
- id: "add-2fa-notify-1"
  content: "Read proposal.md and design.md for add-2fa-notify"
  status: "pending"
  priority: "high"
  
- id: "add-2fa-notify-2"
  content: "Implement OTP generation (tasks.md:1.1) - refs specs/auth/spec.md:5"
  status: "pending"
  priority: "medium"
  
- id: "add-2fa-notify-3"
  content: "Create email notification service (tasks.md:1.2) - refs specs/notifications/spec.md:3"
  status: "pending"
  priority: "medium"
  
- id: "add-2fa-notify-validate"
  content: "Run openspec validate add-2fa-notify --strict and fix any issues"
  status: "pending"
  priority: "high"
```

## Error Handling

### Common Issues and Solutions

#### Issue: `openspec validate` fails
**Solution**: 
1. Check validation output for specific errors
2. Fix formatting issues in spec files
3. Ensure all requirements have scenarios
4. Run `openspec validate --strict` again

#### Issue: Missing spec references
**Solution**:
1. Identify which capability the todo affects
2. Locate the correct spec file
3. Add proper reference format: `specs/{capability}/spec.md:{line-number}`

#### Issue: TODO completion without evidence
**Solution**:
1. Provide concrete evidence (test results, file changes, validation output)
2. Reference specific files and line numbers
3. Show before/after states where applicable

## Best Practices

### TODO Naming
- Use change-ID prefix: `{change-id}-{number}`
- Keep descriptions concise but informative
- Include task number reference: `(tasks.md:1.1)`
- Include spec reference: `refs specs/auth/spec.md:3`

### State Management
- Only one `in_progress` todo at any time
- Use `awaiting_approval` for all subtask completions
- Never mark todos `completed` without user confirmation
- Update todo states immediately after each action

### Validation
- Run `openspec validate` after each significant change
- Always use `--strict` flag for comprehensive checking
- Fix validation errors before proceeding to next task

## Troubleshooting

### Validation Failures
```bash
# Debug specific change
openspec show <change-id> --json --deltas-only

# Check spec formatting
openspec validate --strict

# Debug scenario parsing
openspec show <spec-id> --json
```

### TODO State Conflicts
```bash
# Check current todos
todoread

# Reset stuck todos (use carefully)
todowrite([])  # Only if completely stuck
```

## Version History

### v1.0 (2025-01-15)
- Initial OpenSpec integration
- Added awaiting_approval state
- Defined change-ID-aware todo structure
- Added spec-driven validation requirements
- Created approval gate workflow
- Added comprehensive documentation and examples

## Contributing

To update this workflow:

1. Update `.openspec-todo-config.yml` with configuration changes
2. Update this documentation to reflect new patterns
3. Test the workflow with real OpenSpec changes
4. Update version history with detailed change notes