"""
Integration tests for OVHProvider.

These tests require valid OVH AI credentials. Set the following environment variables:
- OVH_API_KEY: Your OVH AI API key
- OVH_AI_ENDPOINT: The OVH AI endpoint URL

Example:
    export OVH_API_KEY="your-api-key"
    export OVH_AI_ENDPOINT="https://mistral-7b-instruct-v0-3.endpoints.kepler.ovh.ai.cloud.com/v1"
    pytest tests/providers/test_ovh_integration.py -v

Note: OVH AI endpoints are model-specific. Ensure the endpoint matches the model you're testing.
"""

import os

import pytest

from inference_client.base.types import InferenceRequest
from inference_client.providers.ovh import OVHProvider


@pytest.fixture
def ovh_credentials():
    """Get OVH AI credentials from environment variables."""
    api_key = os.environ.get("OVH_API_KEY")
    endpoint = os.environ.get("OVH_AI_ENDPOINT")

    if not api_key or not endpoint:
        pytest.skip("OVH_API_KEY and/or OVH_AI_ENDPOINT environment variables not set")

    return {"api_key": api_key, "endpoint": endpoint}


@pytest.fixture
def provider(ovh_credentials):
    """Create an OVHProvider instance."""
    return OVHProvider(
        api_key=ovh_credentials["api_key"], base_url=ovh_credentials["endpoint"]
    )


@pytest.mark.integration
class TestOVHIntegration:
    """Integration tests for OVHProvider."""

    def test_supported_models_returns_list(self, provider):
        """Test that supported_models returns a non-empty list of model names."""
        models = provider.supported_models()

        assert isinstance(models, list)
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)

    def test_predict_single_message(self, provider):
        """Test that predict returns a valid response for a single message."""

        # models = provider.supported_models()
        # model = models[0]

        request = InferenceRequest(
            model="Mistral-7B-Instruct-v0.3",
            message="Hello, can you respond with a simple greeting?",
        )

        response = provider.predict(request)

        assert response is not None
        assert response.is_valid()
        assert isinstance(response.message, str)
        assert len(response.message) > 0


@pytest.mark.integration
class TestOVHClientIntegration:
    """Integration tests for OVH through InferenceClient."""

    def test_client_predict_through_inference_client(self, ovh_credentials):
        """Test that InferenceClient works with OVH provider."""
        from inference_client import InferenceClient, InferenceRequest

        # Create client using class method
        client = InferenceClient.create_ovh_client(
            api_key=ovh_credentials["api_key"], base_url=ovh_credentials["endpoint"]
        )

        # Get available models from the provider
        models = client.provider.models
        assert len(models) > 0, "No models available from OVH AI"
        model = models[0]

        request = InferenceRequest(
            model=model,
            message="Hello from InferenceClient integration test",
        )

        response = client.predict(request)

        assert response is not None
        assert response.is_valid()
        assert isinstance(response.message, str)
        assert len(response.message) > 0

    def test_client_predict_with_invalid_model_fails(self, ovh_credentials):
        """Test that InferenceClient fails validation for non-existent model."""
        from inference_client import (
            InferenceClient,
            InferenceRequest,
            InferenceRequestError,
        )

        client = InferenceClient.create_ovh_client(
            api_key=ovh_credentials["api_key"], base_url=ovh_credentials["endpoint"]
        )

        request = InferenceRequest(
            model="non-existent-model-12345",
            message="Hello",
        )

        with pytest.raises(InferenceRequestError) as exc_info:
            client.predict(request)

        assert "not supported by the provider" in str(exc_info.value)
