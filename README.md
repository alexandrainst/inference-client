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

```bash
pip install inference-client
```

## Supported Providers

### Ollama

[Ollama](https://ollama.com/) enables local inference with various open-source models.

**Prerequisites:**
1. Install Ollama from [https://ollama.com/](https://ollama.com/)
2. Start Ollama service: `ollama serve`
3. Pull a model: `ollama pull llama2:7b`

**Usage:**

```python
from inference_client.providers.ollama import OllamaProvider
from inference_client.base.types import InferenceRequest

# Initialize provider (defaults to http://localhost:11434)
provider = OllamaProvider()

# Or with custom configuration
provider = OllamaProvider(host="http://localhost:11434", timeout=60)

# List available models
models = provider.supported_models()
print(f"Available models: {models}")

# Make a prediction
request = InferenceRequest(model="llama2:7b", message="Hello, how are you?")
response = provider.predict(request)
print(response.message)
```

### OpenAI

[OpenAI](https://openai.com/) provides cloud-based inference with GPT models.

**Prerequisites:**
1. Get an API key from [https://platform.openai.com/](https://platform.openai.com/)
2. Set the environment variable: `export OPENAI_API_KEY="sk-..."`

**Usage:**

```python
from inference_client.providers.openai import OpenAIProvider
from inference_client.base.types import InferenceRequest, ContextMessage, Role

# Initialize provider (uses OPENAI_API_KEY environment variable)
provider = OpenAIProvider()

# Or with explicit API key
provider = OpenAIProvider(api_key="sk-...", timeout=60)

# List available models
models = provider.supported_models()
print(f"Available models: {models}")

# Make a prediction
request = InferenceRequest(model="gpt-4o-mini", message="Hello, how are you?")
response = provider.predict(request)
print(response.message)

# Multi-turn conversation with context
context = [
    ContextMessage(role=Role.USER, content="My name is Alice."),
    ContextMessage(role=Role.ASSISTANT, content="Nice to meet you, Alice!"),
]
request = InferenceRequest(
    model="gpt-4o-mini",
    message="What's my name?",
    context=context,
)
response = provider.predict(request)
print(response.message)  # Will remember the name from context
```

## Error Handling

All providers use consistent exception types:

```python
from inference_client.exceptions import (
    ConfigurationError,      # Invalid configuration (API key, URL, etc.)
    InferenceRequestError,   # Request failed (model not found, rate limit, etc.)
    InferenceTimeoutError,   # Request timed out
)

try:
    response = provider.predict(request)
except ConfigurationError as e:
    print(f"Configuration issue: {e}")
except InferenceTimeoutError as e:
    print(f"Request timed out: {e}")
except InferenceRequestError as e:
    print(f"Request failed: {e}")
```


## Contributing

This project uses OpenSpec for spec-driven development. See [AGENTS.md](AGENTS.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
