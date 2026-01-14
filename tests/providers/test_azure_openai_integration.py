"""
Integration tests for AzureOpenAIProvider.

These tests require valid Azure OpenAI credentials. Set the following
environment variables to run these tests:

    export AZURE_OPENAI_API_KEY="your-api-key"
    export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

You also need a deployed model in your Azure OpenAI resource.

Example:
    pytest tests/providers/test_azure_openai_integration.py -v
"""

import os

import pytest

from inference_client.base.types import InferenceRequest
from inference_client.providers.azure_openai import AzureOpenAIProvider


@pytest.fixture
def provider():
    """Create an AzureOpenAIProvider instance using environment variables."""
    if not os.environ.get("AZURE_OPENAI_API_KEY"):
        pytest.skip("AZURE_OPENAI_API_KEY environment variable not set")
    if not os.environ.get("AZURE_OPENAI_ENDPOINT"):
        pytest.skip("AZURE_OPENAI_ENDPOINT environment variable not set")
    return AzureOpenAIProvider()


@pytest.fixture
def deployment_name():
    """Get the deployment name to use for tests."""
    # You can set this environment variable to specify a deployment name
    # Default to a common deployment name pattern
    return os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")


@pytest.mark.integration
class TestAzureOpenAIIntegration:
    """Integration tests for AzureOpenAIProvider."""

    def test_supported_models_returns_empty_list(self, provider):
        """Test that supported_models returns an empty list (Azure limitation)."""
        models = provider.supported_models()

        assert isinstance(models, list)
        assert len(models) == 0  # Azure OpenAI doesn't expose deployment listing

    def test_predict_single_message(self, provider, deployment_name):
        """Test that predict returns a valid response for a single message."""
        request = InferenceRequest(
            model=deployment_name,
            message="Say 'hello' and nothing else.",
        )

        response = provider.predict(request)

        assert response is not None
        assert response.is_valid()
        assert isinstance(response.message, str)
        assert len(response.message) > 0
