## Context
The inference-client project is a Python library that provides a unified API for different inference providers. Currently, the project lacks proper Python packaging configuration, making it impossible for users to install via pip from the GitHub repository. This limits distribution and adoption of the library.

The project uses:
- Python 3.14+ as the target runtime
- src layout for package organization
- pytest for testing
- Ruff for linting and formatting
- VS Code devcontainer for development

## Goals / Non-Goals
- Goals:
  - Enable `pip install git+https://github.com/your-org/inference-client.git` functionality
  - Provide proper version management via git tags
  - Support both runtime and development dependency management
  - Integrate with existing CI/CD pipeline for build validation
  - Maintain compatibility with current project structure and tools
- Non-Goals:
  - Breaking changes to existing API or structure
  - Migration away from current tooling (ruff, pytest, etc.)
  - Support for Python versions below 3.14
  - Publishing to PyPI or other package repositories
  - Complex distribution mechanisms (conda, etc.)

## Decisions
- Decision: Use `pyproject.toml` as the primary configuration file
  - **Why**: Modern Python packaging standard, supports all required metadata and build configuration
  - **Alternatives considered**: setup.py (legacy), setup.cfg (limited), poetry (additional complexity)
  
- Decision: Use `setuptools` with `setuptools-scm` for build system
  - **Why**: Proven, widely compatible, integrates well with existing project structure
  - **Alternatives considered**: hatch (newer but less battle-tested), flit (simpler but less flexible), poetry (opinionated, requires workflow changes)
  
- Decision: Use `setuptools-scm` for version management
  - **Why**: Automatic versioning from git tags, no manual version maintenance
  - **Alternatives considered**: Manual version in __init__.py (error-prone), dynamic version from file (requires manual updates)
  
- Decision: Maintain src layout
  - **Why**: Already established in project, better separation of source from project root
  - **Alternatives considered**: Flat layout (would require restructuring)

## Risks / Trade-offs
- Risk: Dependency version conflicts may arise during packaging setup
  - **Mitigation**: Start with minimal dependencies, use dependency groups for optional features
  
- Risk: Build system complexity may increase maintenance burden
  - **Mitigation**: Use well-documented, standard tools; keep configuration simple
  
- Trade-off: setuptools-scm requires proper git tag hygiene
  - **Benefit**: Automatic version management outweighs the discipline requirement

## Migration Plan
1. **Setup Phase**: Create pyproject.toml with minimal configuration
2. **Testing Phase**: Build and test package locally in clean environments  
3. **Integration Phase**: Update CI/CD pipeline for build validation
4. **Documentation Phase**: Update GitHub installation and development documentation
5. **Usage Phase**: Provide examples for installing specific branches/tags from GitHub

**Rollback**: If issues arise, can remove pyproject.toml and revert to current state without breaking existing functionality.

## Open Questions
- Should we include optional dependencies for specific providers (e.g., openai extra for OpenAI provider)?
  - Leaning toward yes, to keep base installation minimal
- What should be the initial version number for the first release?
  - Should follow semantic versioning based on current API stability
- How should we document installation from specific branches or tags?
  - Should provide clear examples for different use cases in documentation