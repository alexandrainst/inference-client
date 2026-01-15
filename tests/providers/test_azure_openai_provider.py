import os
from unittest.mock import Mock, patch

import openai
import pytest

from inference_client.base.types import (
    ContextMessage,
    InferenceRequest,
    InferenceResponse,
    Role,
)
from inference_client.exceptions import (
    ConfigurationError,
    InferenceRequestError,
    InferenceTimeoutError,
)
from inference_client.providers.azure_openai.azure_openai_provider import (
    AzureOpenAIProvider,
)


@pytest.fixture(autouse=True)
def clear_azure_env():
    """Clear Azure OpenAI env vars before each test to ensure isolation."""
    original_key = os.environ.pop("AZURE_OPENAI_API_KEY", None)
    original_endpoint = os.environ.pop("AZURE_OPENAI_ENDPOINT", None)
    yield
    if original_key:
        os.environ["AZURE_OPENAI_API_KEY"] = original_key
    if original_endpoint:
        os.environ["AZURE_OPENAI_ENDPOINT"] = original_endpoint


class TestAzureOpenAIProvider:
    """Test suite for AzureOpenAIProvider."""

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_init_with_api_key_and_endpoint(self, mock_azure_openai_class):
        """Test provider initialization with API key and endpoint."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )

        assert provider.api_key == "test-api-key"
        assert provider.azure_endpoint == "https://test.openai.azure.com"
        assert provider.api_version == "2024-02-01"
        assert provider.timeout == 60
        mock_azure_openai_class.assert_called_once_with(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2024-02-01",
            timeout=60,
        )

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_init_with_env_vars(self, mock_azure_openai_class):
        """Test provider initialization with environment variables."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        os.environ["AZURE_OPENAI_API_KEY"] = "env-api-key"
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://env-test.openai.azure.com"

        provider = AzureOpenAIProvider()

        assert provider.api_key == "env-api-key"
        assert provider.azure_endpoint == "https://env-test.openai.azure.com"
        mock_azure_openai_class.assert_called_once_with(
            api_key="env-api-key",
            azure_endpoint="https://env-test.openai.azure.com",
            api_version="2024-02-01",
            timeout=60,
        )

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_init_explicit_overrides_env_vars(self, mock_azure_openai_class):
        """Test that explicit parameters override environment variables."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        os.environ["AZURE_OPENAI_API_KEY"] = "env-api-key"
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://env-test.openai.azure.com"

        provider = AzureOpenAIProvider(
            api_key="explicit-api-key",
            azure_endpoint="https://explicit.openai.azure.com",
        )

        assert provider.api_key == "explicit-api-key"
        assert provider.azure_endpoint == "https://explicit.openai.azure.com"
        mock_azure_openai_class.assert_called_once_with(
            api_key="explicit-api-key",
            azure_endpoint="https://explicit.openai.azure.com",
            api_version="2024-02-01",
            timeout=60,
        )

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_init_with_custom_config(self, mock_azure_openai_class):
        """Test provider initialization with custom configuration."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2024-06-01",
            timeout=120,
        )

        assert provider.api_key == "test-api-key"
        assert provider.azure_endpoint == "https://test.openai.azure.com"
        assert provider.api_version == "2024-06-01"
        assert provider.timeout == 120
        mock_azure_openai_class.assert_called_once_with(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
            api_version="2024-06-01",
            timeout=120,
        )

    def test_init_without_api_key_raises_error(self):
        """Test that missing API key raises ConfigurationError."""
        os.environ["AZURE_OPENAI_ENDPOINT"] = "https://test.openai.azure.com"

        with pytest.raises(ConfigurationError) as exc_info:
            AzureOpenAIProvider()

        assert "API key is required" in str(exc_info.value)

    def test_init_with_empty_api_key_raises_error(self):
        """Test that empty API key raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            AzureOpenAIProvider(
                api_key="",
                azure_endpoint="https://test.openai.azure.com",
            )

        assert "API key is required" in str(exc_info.value)

    def test_init_without_endpoint_raises_error(self):
        """Test that missing endpoint raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            AzureOpenAIProvider(api_key="test-api-key")

        assert "Azure endpoint is required" in str(exc_info.value)

    def test_init_with_empty_endpoint_raises_error(self):
        """Test that empty endpoint raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            AzureOpenAIProvider(
                api_key="test-api-key",
                azure_endpoint="",
            )

        assert "Azure endpoint is required" in str(exc_info.value)

    def test_init_with_invalid_endpoint_protocol_raises_error(self):
        """Test that non-https endpoint raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            AzureOpenAIProvider(
                api_key="test-api-key",
                azure_endpoint="http://test.openai.azure.com",
            )

        assert "must start with https://" in str(exc_info.value)

    def test_init_with_invalid_timeout_raises_error(self):
        """Test that invalid timeout raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            AzureOpenAIProvider(
                api_key="test-api-key",
                azure_endpoint="https://test.openai.azure.com",
                timeout=0,
            )

        assert "Timeout must be a positive integer" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_single_message(self, mock_azure_openai_class):
        """Test prediction with a single message."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        # Setup mock response
        mock_message = Mock()
        mock_message.content = "Hello! How can I help you today?"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        response = provider.predict(request)

        assert isinstance(response, InferenceResponse)
        assert response.message == "Hello! How can I help you today?"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4-deployment",
            messages=[{"role": "user", "content": "Hello!"}],
        )

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_with_context(self, mock_azure_openai_class):
        """Test prediction with conversation context."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        # Setup mock response
        mock_message = Mock()
        mock_message.content = "The capital of France is Paris."
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )

        context = [
            ContextMessage(role=Role.USER, content="Hi there!"),
            ContextMessage(role=Role.ASSISTANT, content="Hello! How can I help?"),
        ]
        request = InferenceRequest(
            model="gpt-4-deployment",
            message="What is the capital of France?",
            context=context,
        )

        response = provider.predict(request)

        assert response.message == "The capital of France is Paris."
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4-deployment",
            messages=[
                {"role": "user", "content": "Hi there!"},
                {"role": "assistant", "content": "Hello! How can I help?"},
                {"role": "user", "content": "What is the capital of France?"},
            ],
        )

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_empty_model_raises_error(self, mock_azure_openai_class):
        """Test that empty deployment name raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Deployment name is required" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_empty_message_raises_error(self, mock_azure_openai_class):
        """Test that empty message raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Message is required" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_authentication_error(self, mock_azure_openai_class):
        """Test that authentication error raises ConfigurationError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Invalid API key",
            response=Mock(status_code=401),
            body=None,
        )

        provider = AzureOpenAIProvider(
            api_key="invalid-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        with pytest.raises(ConfigurationError) as exc_info:
            provider.predict(request)

        assert "Invalid API key" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_rate_limit_error(self, mock_azure_openai_class):
        """Test that rate limit error raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit exceeded",
            response=Mock(status_code=429),
            body=None,
        )

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Rate limit exceeded" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_deployment_not_found_error(self, mock_azure_openai_class):
        """Test that deployment not found error raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.NotFoundError(
            message="Deployment not found",
            response=Mock(status_code=404),
            body=None,
        )

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="invalid-deployment", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "not found" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_bad_request_error(self, mock_azure_openai_class):
        """Test that bad request error raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.BadRequestError(
            message="Invalid request",
            response=Mock(status_code=400),
            body=None,
        )

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Invalid request" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_timeout_error(self, mock_azure_openai_class):
        """Test that timeout error raises InferenceTimeoutError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError(
            request=Mock()
        )

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        with pytest.raises(InferenceTimeoutError) as exc_info:
            provider.predict(request)

        assert "timed out" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_connection_error(self, mock_azure_openai_class):
        """Test that connection error raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=Mock()
        )

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Failed to connect" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_predict_empty_response_raises_error(self, mock_azure_openai_class):
        """Test that empty response raises InferenceRequestError."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )
        request = InferenceRequest(model="gpt-4-deployment", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Invalid response" in str(exc_info.value)

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_supported_models_returns_empty_list(self, mock_azure_openai_class):
        """Test that supported_models returns an empty list for Azure OpenAI."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )

        models = provider.supported_models()

        assert models == []

    @patch("inference_client.providers.azure_openai.azure_openai_provider.AzureOpenAI")
    def test_models_property_returns_empty_list(self, mock_azure_openai_class):
        """Test that models property returns an empty list."""
        mock_client = Mock()
        mock_azure_openai_class.return_value = mock_client

        provider = AzureOpenAIProvider(
            api_key="test-api-key",
            azure_endpoint="https://test.openai.azure.com",
        )

        # Access models property
        models = provider.models

        assert models == []
