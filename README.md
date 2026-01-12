# Inference Client

A Python library that provides one unified API to call different inference providers. This project simplifies the integration of various AI/ML inference services by providing a consistent interface, reducing the complexity of switching between different providers or using multiple providers simultaneously.

## Features

- **Unified API**: Single interface for multiple inference providers
- **Local & Cloud Support**: Work with both local models (Ollama) and cloud services (OpenAI, etc.)
- **Chat-based Interactions**: Multi-turn conversation support with context management
- **Robust Error Handling**: Comprehensive error handling with actionable feedback
- **Type Safety**: Full type hints and validation
- **Async Support**: Both synchronous and asynchronous operations
- **Extensible**: Easy to add new inference providers

## Installation

```bash
pip install inference-client
```

## Quick Start

### Using Ollama (Local Inference)

```python
from inference_client.providers.ollama import OllamaProvider
from inference_client.base.types import InferenceRequest

# Initialize Ollama provider
provider = OllamaProvider()

# Make a prediction
request = InferenceRequest(
    model="llama2:7b",
    message="What is machine learning?"
)

response = provider.predict(request)
print(response.message)
```

### Multi-turn Conversations

```python
# First exchange
request1 = InferenceRequest(
    model="llama2:7b",
    message="Hello, I'm learning Python. What's a good first project?"
)
response1 = provider.predict(request1)

# Follow-up with context
request2 = InferenceRequest(
    model="llama2:7b",
    message="How long would that take?",
    context=[request1.message, response1.message]
)
response2 = provider.predict(request2)
```

### Async Operations

```python
import asyncio

async def async_predict():
    provider = OllamaProvider()
    request = InferenceRequest(model="llama2:7b", message="Hello!")
    response = await provider.predict_async(request)
    return response.message

# Run async
result = asyncio.run(async_predict())
```

## Supported Providers

### Ollama

[Ollama](https://ollama.com/) enables local inference with various open-source models.

**Prerequisites:**
1. Install Ollama from [https://ollama.com/](https://ollama.com/)
2. Start Ollama service: `ollama serve`
3. Pull a model: `ollama pull llama2:7b`

**Configuration:**
```python
from inference_client.providers.ollama import OllamaProvider

# Default (localhost:11434)
provider = OllamaProvider()

# Custom configuration
provider = OllamaProvider(
    host="http://remote-server:11434",
    timeout=60
)
```

**Available Models:**
```python
models = provider.supported_models()
print(f"Available models: {models}")
```

### OpenAI (Coming Soon)

OpenAI GPT models support will be available in future releases.

## Error Handling

The library provides specific exceptions for different scenarios:

```python
from inference_client.exceptions import (
    InferenceRequestError,
    InferenceTimeoutError,
    ConfigurationError
)

try:
    response = provider.predict(request)
except InferenceRequestError as e:
    if "Cannot connect" in str(e):
        print("Service unavailable - check if Ollama is running")
    elif "not found" in str(e):
        print("Model not available - try: ollama pull <model-name>")
except InferenceTimeoutError:
    print("Request timed out - try increasing timeout or using smaller model")
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

## Development

### Running Tests

```bash
# Unit tests only
python -m pytest tests/ -m "not integration"

# All tests (requires running Ollama)
python -m pytest tests/

# With coverage
python -m pytest tests/ --cov=src/inference_client --cov-report=html
```

### Integration Tests

Integration tests require a running Ollama instance:

```bash
# Start Ollama
ollama serve

# Pull test model
ollama pull llama2:7b

# Run integration tests
python -m pytest tests/ -m integration
```

## Documentation

Detailed documentation for each provider:

- [Ollama Provider Guide](docs/providers/ollama.md)
- [Examples](examples/)

## Contributing

This project uses OpenSpec for spec-driven development. See [AGENTS.md](AGENTS.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
