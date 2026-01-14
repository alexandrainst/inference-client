"""
Integration tests for OpenAIProvider.

These tests require a valid OpenAI API key. Set the OPENAI_API_KEY
environment variable to run these tests.

Example:
    export OPENAI_API_KEY="sk-..."
    pytest tests/providers/test_openai_integration.py -v
"""

import os

import pytest

from inference_client.base.types import InferenceRequest
from inference_client.providers.openai import OpenAIProvider


@pytest.fixture
def provider():
    """Create an OpenAIProvider instance using the environment variable."""
    if not os.environ.get("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY environment variable not set")
    return OpenAIProvider()


@pytest.mark.integration
class TestOpenAIIntegration:
    """Integration tests for OpenAIProvider."""

    def test_supported_models_returns_list(self, provider):
        """Test that supported_models returns a non-empty list of model names."""
        models = provider.supported_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)
        # Should include common models
        model_ids = [m.lower() for m in models]
        assert any("gpt" in m for m in model_ids), "Expected GPT models in the list"

    def test_predict_single_message(self, provider):
        """Test that predict returns a valid response for a single message."""
        # Get available models first
        models = provider.supported_models()
        model = models[0]

        request = InferenceRequest(
            model=model,
            message="Say 'hello' and nothing else.",
        )

        response = provider.predict(request)

        assert response is not None
        assert response.is_valid()
        assert isinstance(response.message, str)
        assert len(response.message) > 0
