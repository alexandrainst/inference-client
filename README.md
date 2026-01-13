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

### OpenAI (Coming Soon)

OpenAI GPT models support will be available in future releases.


## Contributing

This project uses OpenSpec for spec-driven development. See [AGENTS.md](AGENTS.md) for contribution guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.
