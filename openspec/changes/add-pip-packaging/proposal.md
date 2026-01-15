# Change: Add pip packaging support

## Why
The project currently lacks proper Python packaging configuration, making it impossible for users to install the library via pip from the GitHub repository. This limits distribution and adoption of the inference client library.

## What Changes
- Add `pyproject.toml` with modern Python packaging configuration
- Configure package metadata, dependencies, and build system
- Set up automatic version management
- Configure development dependencies and optional dependencies
- Add packaging to CI/CD pipeline for build validation (no publishing)

## Impact
- Affected specs: packaging (new capability)
- Affected code: Root directory (add pyproject.toml), potentially __init__.py for version management
- Enables: `pip install git+https://github.com/your-org/inference-client.git` functionality