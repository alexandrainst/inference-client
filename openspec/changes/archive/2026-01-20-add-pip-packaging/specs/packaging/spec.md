## ADDED Requirements
### Requirement: PyProject.toml Configuration
The system SHALL include a `pyproject.toml` file that defines the package build configuration, metadata, and dependencies.

#### Scenario: Basic package installation
- **WHEN** a user runs `pip install git+https://github.com/your-org/inference-client.git`
- **THEN** the package SHALL install successfully with all required dependencies
- **AND** the package SHALL be importable as `import inference_client`

#### Scenario: Package metadata validation
- **WHEN** the package is built or installed
- **THEN** all required metadata SHALL be present (name, version, description, author)
- **AND** the package SHALL comply with PyPI standards

### Requirement: Dependency Management
The system SHALL properly declare runtime and development dependencies.

#### Scenario: Runtime dependencies installation
- **WHEN** the package is installed
- **THEN** all required runtime dependencies SHALL be automatically installed
- **AND** the package SHALL work without additional dependency installation

#### Scenario: Development dependencies isolation
- **WHEN** developers install with development extras
- **THEN** development tools (pytest, ruff, etc.) SHALL be available
- **AND** runtime dependencies SHALL NOT be polluted with dev-only packages

### Requirement: Version Management
The system SHALL provide automatic version management for releases.

#### Scenario: Version detection
- **WHEN** the package is built
- **THEN** version SHALL be automatically determined from git tags
- **AND** development versions SHALL include appropriate suffixes

#### Scenario: Version accessibility
- **WHEN** the package is imported
- **THEN** version SHALL be accessible via `inference_client.__version__`
- **AND** version SHALL match the installed package version

### Requirement: Build System Integration
The system SHALL integrate with modern Python build tools.

#### Scenario: Local package building
- **WHEN** developers run build commands
- **THEN** the package SHALL build successfully into wheel and sdist formats
- **AND** build artifacts SHALL pass validation

#### Scenario: CI/CD pipeline integration
- **WHEN** automated builds run in CI
- **THEN** the package SHALL build consistently across environments
- **AND** build failures SHALL provide clear error messages

#### Scenario: GitHub installation validation
- **WHEN** users install from the GitHub repository URL
- **THEN** the package SHALL install correctly from any branch or tag
- **AND** version information SHALL be properly derived from git context