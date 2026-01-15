<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## TODO Workflow Enhancement

**MANDATORY**: Always read `.openspec-todo-config.yml` before creating any TODOs in this project.

### Enhanced TODO Workflow

This project uses OpenSpec-enhanced TODO workflow with these additional requirements:

1. **Read Configuration First**: Always read `.openspec-todo-config.yml` for workflow rules
2. **Change-ID-Aware Naming**: Use `{change-id}-{number}` format when implementing OpenSpec changes
3. **Spec References**: Include `refs specs/{capability}/spec.md:{line-number}` in TODO content
4. **Approval Gates**: Use `awaiting_approval` state for subtask completions
5. **Validation Required**: Run `scripts/validate-todo-workflow.sh` before completing changes

### When to Use Enhanced Workflow

Use the enhanced TODO workflow when:
- Implementing any OpenSpec change proposal
- Working with existing active changes (`openspec list`)
- Creating TODOs that relate to spec requirements
- Any task involves specs, proposals, or architectural changes

### Quick Reference

- **Configuration**: `.openspec-todo-config.yml`
- **Documentation**: `docs/openspec-todo-workflow.md`
- **Validation**: `scripts/validate-todo-workflow.sh`

### Example Workflow

```bash
# Before starting any work
read .openspec-todo-config.yml
openspec list  # Check for active changes

# Create enhanced TODOs if working on changes
todowrite([
  {
    id: "add-feature-1",
    content: "Task description (tasks.md:1.1) - refs specs/feature/spec.md:3",
    status: "pending"
  }
])

# Validate workflow
./scripts/validate-todo-workflow.sh
```