# Inference Client

A Python library that provides one unified API to call different inference providers. This project simplifies the integration of various AI/ML inference services by providing a consistent interface, reducing the complexity of switching between different providers or using multiple providers simultaneously.

## Features

- **Unified API**: Single interface for multiple inference providers
- **Local & Cloud Support**: Work with both local models (Ollama) and cloud services (OpenAI, etc.)
- **Chat-based Interactions**: Multi-turn conversation support with context management
- **Robust Error Handling**: Comprehensive error handling with actionable feedback
- **Type Safety**: Full type hints and validation
- **Extensible**: Easy to add new inference providers

## Installation

### From PyPI (when published)

```bash
pip install inference-client
```

### From GitHub (development version)

```bash
# Install latest main branch
pip install git+https://github.com/your-org/inference-client.git

# Install specific branch
pip install git+https://github.com/your-org/inference-client.git@develop

# Install specific tag/release
pip install git+https://github.com/your-org/inference-client.git@v1.0.0

# Install specific commit
pip install git+https://github.com/your-org/inference-client.git@a1b2c3d
```

### Install with optional dependencies

```bash
# Install with OpenAI support
pip install "inference-client[openai]"

# Install with development dependencies
pip install "inference-client[dev]"

# Install all optional dependencies
pip install "inference-client[all]"
```

## Supported Providers

### Ollama

[Ollama](https://ollama.com/) enables local inference with various open-source models.

**Prerequisites:**
1. Install Ollama from [https://ollama.com/](https://ollama.com/)
2. Start Ollama service: `ollama serve`
3. Pull a model: `ollama pull llama2:7b`

### OpenAI

OpenAI GPT models support is available when installed with the `openai` extra:

```bash
pip install "inference-client[openai]"
```


### Building the package

```bash
# Build source distribution and wheel
python -m build --sdist --wheel --outdir dist

# Validate the package
check-wheel-contents dist/*.whl
twine check dist/*
```

### Testing

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=inference_client --cov-report=html

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py

# Run tests with coverage and generate report
pytest --cov=inference_client --cov-report=html --cov-report=term


### Version management

This project uses [setuptools-scm](https://github.com/pypa/setuptools_scm) for automatic version management from git tags:

```bash
# Create a release tag
git tag v1.0.0
git push origin v1.0.0

# Development version (automatically generated)
# Format: 1.0.0.devN+gHASH.dDATE
```

## Contributing

This project uses OpenSpec for spec-driven development. See [AGENTS.md](AGENTS.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
