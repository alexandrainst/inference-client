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
from inference_client.providers.openai.openai_provider import OpenAIProvider


@pytest.fixture(autouse=True)
def clear_openai_env():
    """Clear OPENAI_API_KEY env var before each test to ensure isolation."""
    original = os.environ.pop("OPENAI_API_KEY", None)
    yield
    if original:
        os.environ["OPENAI_API_KEY"] = original


class TestOpenAIProvider:
    """Test suite for OpenAIProvider."""

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_init_with_api_key(self, mock_openai_class):
        """Test provider initialization with API key."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test-api-key")

        assert provider.api_key == "test-api-key"
        assert provider.base_url is None
        assert provider.timeout == 60
        mock_openai_class.assert_called_once_with(
            api_key="test-api-key",
            base_url=None,
            timeout=60,
        )

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_init_with_env_var(self, mock_openai_class):
        """Test provider initialization with OPENAI_API_KEY environment variable."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        os.environ["OPENAI_API_KEY"] = "env-api-key"

        provider = OpenAIProvider()

        assert provider.api_key == "env-api-key"
        mock_openai_class.assert_called_once_with(
            api_key="env-api-key",
            base_url=None,
            timeout=60,
        )

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_init_api_key_overrides_env_var(self, mock_openai_class):
        """Test that explicit api_key overrides environment variable."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        os.environ["OPENAI_API_KEY"] = "env-api-key"

        provider = OpenAIProvider(api_key="explicit-api-key")

        assert provider.api_key == "explicit-api-key"
        mock_openai_class.assert_called_once_with(
            api_key="explicit-api-key",
            base_url=None,
            timeout=60,
        )

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_init_with_custom_config(self, mock_openai_class):
        """Test provider initialization with custom configuration."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(
            api_key="test-api-key",
            base_url="https://custom-api.example.com",
            timeout=120,
        )

        assert provider.api_key == "test-api-key"
        assert provider.base_url == "https://custom-api.example.com"
        assert provider.timeout == 120
        mock_openai_class.assert_called_once_with(
            api_key="test-api-key",
            base_url="https://custom-api.example.com",
            timeout=120,
        )

    def test_init_without_api_key_raises_error(self):
        """Test that empty API key raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIProvider(api_key="")

        assert "API key is required" in str(exc_info.value)

    def test_init_with_no_api_key_and_no_env_raises_error(self):
        """Test that missing API key and no env var raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIProvider()

        assert "API key is required" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_init_with_invalid_base_url_raises_error(self, mock_openai_class):
        """Test that invalid base URL raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIProvider(api_key="test-key", base_url="invalid-url")

        assert "Base URL must start with http://" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_init_with_invalid_timeout_raises_error(self, mock_openai_class):
        """Test that invalid timeout raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            OpenAIProvider(api_key="test-key", timeout=0)

        assert "Timeout must be a positive integer" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_single_message(self, mock_openai_class):
        """Test prediction with a single message."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Setup mock response
        mock_message = Mock()
        mock_message.content = "Hello! How can I help you today?"
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        response = provider.predict(request)

        assert isinstance(response, InferenceResponse)
        assert response.message == "Hello! How can I help you today?"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello!"}],
        )

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_with_context(self, mock_openai_class):
        """Test prediction with conversation context."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Setup mock response
        mock_message = Mock()
        mock_message.content = "The capital of France is Paris."
        mock_choice = Mock()
        mock_choice.message = mock_message
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-api-key")

        context = [
            ContextMessage(role=Role.USER, content="Hi there!"),
            ContextMessage(role=Role.ASSISTANT, content="Hello! How can I help?"),
        ]
        request = InferenceRequest(
            model="gpt-4",
            message="What is the capital of France?",
            context=context,
        )

        response = provider.predict(request)

        assert response.message == "The capital of France is Paris."
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Hi there!"},
                {"role": "assistant", "content": "Hello! How can I help?"},
                {"role": "user", "content": "What is the capital of France?"},
            ],
        )

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_empty_model_raises_error(self, mock_openai_class):
        """Test that empty model name raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Model name is required" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_empty_message_raises_error(self, mock_openai_class):
        """Test that empty message raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="gpt-4", message="")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Message is required" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_authentication_error(self, mock_openai_class):
        """Test that authentication error raises ConfigurationError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Invalid API key",
            response=Mock(status_code=401),
            body=None,
        )

        provider = OpenAIProvider(api_key="invalid-key")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(ConfigurationError) as exc_info:
            provider.predict(request)

        assert "Invalid API key" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_rate_limit_error(self, mock_openai_class):
        """Test that rate limit error raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limit exceeded",
            response=Mock(status_code=429),
            body=None,
        )

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Rate limit exceeded" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_model_not_found_error(self, mock_openai_class):
        """Test that model not found error raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.NotFoundError(
            message="Model not found",
            response=Mock(status_code=404),
            body=None,
        )

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="invalid-model", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "not found" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_timeout_error(self, mock_openai_class):
        """Test that timeout error raises InferenceTimeoutError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APITimeoutError(
            request=Mock()
        )

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(InferenceTimeoutError) as exc_info:
            provider.predict(request)

        assert "timed out" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_connection_error(self, mock_openai_class):
        """Test that connection error raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=Mock()
        )

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Failed to connect" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_predict_empty_response_raises_error(self, mock_openai_class):
        """Test that empty response raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        provider = OpenAIProvider(api_key="test-api-key")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.predict(request)

        assert "Invalid response" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_supported_models(self, mock_openai_class):
        """Test retrieving supported models."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Setup mock response
        mock_model1 = Mock()
        mock_model1.id = "gpt-4"
        mock_model2 = Mock()
        mock_model2.id = "gpt-3.5-turbo"
        mock_model3 = Mock()
        mock_model3.id = "gpt-4o"
        mock_response = Mock()
        mock_response.data = [mock_model1, mock_model2, mock_model3]
        mock_client.models.list.return_value = mock_response

        provider = OpenAIProvider(api_key="test-api-key")
        models = provider.supported_models()

        assert "gpt-4" in models
        assert "gpt-3.5-turbo" in models
        assert "gpt-4o" in models
        mock_client.models.list.assert_called_once()

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_supported_models_authentication_error(self, mock_openai_class):
        """Test that authentication error in models list raises ConfigurationError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_client.models.list.side_effect = openai.AuthenticationError(
            message="Invalid API key",
            response=Mock(status_code=401),
            body=None,
        )

        provider = OpenAIProvider(api_key="invalid-key")

        with pytest.raises(ConfigurationError) as exc_info:
            provider.supported_models()

        assert "Invalid API key" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_supported_models_empty_response(self, mock_openai_class):
        """Test that empty models response raises InferenceRequestError."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        mock_response = Mock()
        mock_response.data = []
        mock_client.models.list.return_value = mock_response

        provider = OpenAIProvider(api_key="test-api-key")

        with pytest.raises(InferenceRequestError) as exc_info:
            provider.supported_models()

        assert "No models available" in str(exc_info.value)

    @patch("inference_client.providers.openai.openai_provider.OpenAI")
    def test_models_property_caches_result(self, mock_openai_class):
        """Test that models property caches the result."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_model = Mock()
        mock_model.id = "gpt-4"
        mock_response = Mock()
        mock_response.data = [mock_model]
        mock_client.models.list.return_value = mock_response

        provider = OpenAIProvider(api_key="test-api-key")

        # Access models property twice
        _ = provider.models
        _ = provider.models

        # Should only call list() once due to caching
        assert mock_client.models.list.call_count == 1
