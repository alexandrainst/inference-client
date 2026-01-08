# Project Context

## Purpose
A Python library that provides one unified API to call different inference providers. This project aims to simplify the integration of various AI/ML inference services by providing a consistent interface, reducing the complexity of switching between different providers or using multiple providers simultaneously.

## Tech Stack
- **Python 3.14** (primary language)
- **Development Environment**: VS Code dev container (Debian GNU/Linux 13 trixie)
- **Code Quality**: Ruff (formatting, linting, import organization)
- **Language Server**: Pylance
- **Testing**: pytest
- **Specification Management**: OpenSpec for spec-driven development
- **Version Control**: Git with GitHub

## Project Conventions

### Code Style
- **Formatter**: Ruff (automatically formats on save)
- **Linter**: Ruff with native server enabled
- **Import Organization**: Automatic import sorting via Ruff
- **Fix All**: Enabled on save for automatic code fixes
- **Type Hints**: Required (Pylance provides type checking)
- **Python Path**: `/usr/local/bin/python`

### Architecture Patterns
- **Unified API Design**: Single interface abstracting multiple inference providers
- **Provider Pattern**: Pluggable architecture for different inference services
- **Spec-Driven Development**: Using OpenSpec for change proposals and feature planning
- **Containerized Development**: Dev container for consistent development environment

### Testing Strategy
- **Framework**: pytest (`/usr/local/py-utils/bin/pytest`)
- **Coverage**: Coverage reports expected (based on gitignore patterns)
- **Hypothesis**: Property-based testing supported
- **Test Organization**: Standard Python test structure

### Git Workflow
- **OpenSpec Integration**: Change proposals required for new features and breaking changes
- **Branching**: Follow OpenSpec three-stage workflow (create proposal → implement → deploy)
- **Validation**: `openspec validate --strict` required before implementation
- **Change IDs**: Kebab-case, verb-led naming (add-, update-, remove-, refactor-)

## Domain Context
- **AI/ML Inference**: Understanding of various AI inference providers and their APIs
- **API Abstraction**: Knowledge of creating unified interfaces across heterogeneous services
- **Provider Integration**: Experience with different inference service patterns (REST APIs, streaming, batch processing)
- **Library Design**: Python library development best practices for developer experience

## Important Constraints
- **Python Version**: Requires Python 3.14+
- **OpenSpec Compliance**: All significant changes must go through OpenSpec proposal process
- **Provider Compatibility**: Must maintain unified interface regardless of underlying provider differences
- **Developer Experience**: API should be simple and consistent across all supported providers

## External Dependencies
- **Inference Providers**: Various AI/ML inference services (to be integrated)
- **OpenSpec CLI**: `@fission-ai/openspec` for specification management
- **Development Tools**: npm ecosystem for tooling, VS Code extensions
- **Container Registry**: Microsoft Dev Container images (`mcr.microsoft.com/devcontainers/python`)
