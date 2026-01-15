"""
Integration tests for OllamaProvider.

These tests require a running Ollama server. Set the OLLAMA_SERVER
environment variable to the full URL of the Ollama server to use.

Example:
    export OLLAMA_SERVER="http://localhost:11434"
    pytest tests/providers/test_ollama_integration.py -v
"""

import os

import pytest

from inference_client.base.types import InferenceRequest
from inference_client.providers.ollama import OllamaProvider


@pytest.fixture
def ollama_server():
    """Get Ollama server URL from environment variable."""
    server = os.environ.get("OLLAMA_SERVER")
    if not server:
        pytest.skip("OLLAMA_SERVER environment variable not set")
    return server


@pytest.fixture
def provider(ollama_server):
    """Create an OllamaProvider instance."""
    return OllamaProvider(host=ollama_server)


@pytest.mark.integration
class TestOllamaIntegration:
    """Integration tests for OllamaProvider."""

    def test_supported_models_returns_list(self, provider):
        """Test that supported_models returns a non-empty list of model names."""
        models = provider.supported_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)

    def test_predict_returns_response(self, provider):
        """Test that predict returns a valid response."""
        # Get available models first
        models = provider.supported_models()
        model = models[0]

        request = InferenceRequest(
            model=model,
            message="Hello",
        )

        response = provider.predict(request)

        assert response is not None
        assert response.is_valid()
        assert isinstance(response.message, str)
        assert len(response.message) > 0


@pytest.mark.integration
class TestOllamaClientIntegration:
    """Integration tests for Ollama through InferenceClient."""

    def test_client_predict_through_inference_client(self, ollama_server):
        """Test that InferenceClient works with Ollama provider."""
        from inference_client import InferenceClient, InferenceRequest

        # Create client using class method
        client = InferenceClient.create_ollama_client(host=ollama_server)

        # Get available models from the provider
        models = client.provider.models
        assert len(models) > 0, "No models available on Ollama server"
        model = models[0]

        request = InferenceRequest(
            model=model,
            message="Hello",
        )

        response = client.predict(request)

        assert response is not None
        assert response.is_valid()
        assert isinstance(response.message, str)
        assert len(response.message) > 0

    def test_client_predict_with_invalid_model_fails(self, ollama_server):
        """Test that InferenceClient fails validation for non-existent model."""
        from inference_client import (
            InferenceClient,
            InferenceRequest,
            InferenceRequestError,
        )

        client = InferenceClient.create_ollama_client(host=ollama_server)

        request = InferenceRequest(
            model="non-existent-model-12345",
            message="Hello",
        )

        with pytest.raises(InferenceRequestError) as exc_info:
            client.predict(request)

        assert "not supported by the provider" in str(exc_info.value)
