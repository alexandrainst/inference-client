import os
from unittest.mock import Mock, patch

import openai
import pytest

from inference_client.base.types import (
    ContextMessage,
    InferenceRequest,
    Role,
)
from inference_client.exceptions import (
    ConfigurationError,
    InferenceRequestError,
    InferenceTimeoutError,
)
from inference_client.providers.ovh.ovh_provider import OVHProvider


@pytest.fixture(autouse=True)
def clear_ovh_env():
    """Clear OVH AI env vars before each test to ensure isolation."""
    original_key = os.environ.pop("OVH_API_KEY", None)
    original_endpoint = os.environ.pop("OVH_AI_ENDPOINT", None)
    yield
    if original_key:
        os.environ["OVH_API_KEY"] = original_key
    if original_endpoint:
        os.environ["OVH_AI_ENDPOINT"] = original_endpoint


class TestOVHProvider:
    """Test suite for OVHProvider."""

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_init_with_api_key_and_endpoint(self, mock_openai_class):
        """Test provider initialization with API key and endpoint."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        provider = OVHProvider(
            api_key="test-api-key",
            base_url="https://ovh-ai.example.com/v1",
        )

        assert provider.api_key == "test-api-key"
        assert provider.base_url == "https://ovh-ai.example.com/v1"
        assert provider.timeout == 60
        mock_openai_class.assert_called_once_with(
            api_key="test-api-key",
            base_url="https://ovh-ai.example.com/v1",
            timeout=60,
        )

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_init_with_env_vars(self, mock_openai_class):
        """Test provider initialization with environment variables."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        os.environ["OVH_API_KEY"] = "env-api-key"
        os.environ["OVH_AI_ENDPOINT"] = "https://env-ovh-ai.example.com/v1"

        provider = OVHProvider()

        assert provider.api_key == "env-api-key"
        assert provider.base_url == "https://env-ovh-ai.example.com/v1"
        mock_openai_class.assert_called_once_with(
            api_key="env-api-key",
            base_url="https://env-ovh-ai.example.com/v1",
            timeout=60,
        )

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_init_explicit_overrides_env_vars(self, mock_openai_class):
        """Test that explicit parameters override environment variables."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client
        os.environ["OVH_API_KEY"] = "env-api-key"
        os.environ["OVH_AI_ENDPOINT"] = "https://env-ovh-ai.example.com/v1"

        provider = OVHProvider(
            api_key="explicit-api-key",
            base_url="https://explicit-ovh-ai.example.com/v1",
        )

        assert provider.api_key == "explicit-api-key"
        assert provider.base_url == "https://explicit-ovh-ai.example.com/v1"
        mock_openai_class.assert_called_once_with(
            api_key="explicit-api-key",
            base_url="https://explicit-ovh-ai.example.com/v1",
            timeout=60,
        )

    def test_init_missing_api_key(self):
        """Test initialization fails with missing API key."""
        with pytest.raises(ConfigurationError, match="API key is required"):
            OVHProvider(api_key=None, base_url="https://test.com")

    def test_init_empty_api_key(self):
        """Test initialization fails with empty API key."""
        with pytest.raises(ConfigurationError, match="API key cannot be empty"):
            OVHProvider(api_key="", base_url="https://test.com")

    def test_init_invalid_api_key_type(self):
        """Test initialization fails with invalid API key type."""
        with pytest.raises(ConfigurationError, match="API key is required"):
            OVHProvider(api_key=123, base_url="https://test.com")

    def test_init_missing_base_url(self):
        """Test initialization fails with missing base URL."""
        with pytest.raises(ConfigurationError, match="Base URL is required"):
            OVHProvider(api_key="test-key", base_url=None)

    def test_init_empty_base_url(self):
        """Test initialization fails with empty base URL."""
        with pytest.raises(ConfigurationError, match="Base URL cannot be empty"):
            OVHProvider(api_key="test-key", base_url="")

    def test_init_invalid_base_url_type(self):
        """Test initialization fails with invalid base URL type."""
        with pytest.raises(ConfigurationError, match="Base URL is required"):
            OVHProvider(api_key="test-key", base_url=123)

    def test_init_base_url_without_https(self):
        """Test initialization fails with base URL not starting with https."""
        with pytest.raises(
            ConfigurationError, match="Base URL must start with https://"
        ):
            OVHProvider(api_key="test-key", base_url="http://test.com")

    def test_init_invalid_timeout(self):
        """Test initialization fails with invalid timeout."""
        with pytest.raises(
            ConfigurationError, match="Timeout must be a positive integer"
        ):
            OVHProvider(api_key="test-key", base_url="https://test.com", timeout=0)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_init_client_creation_failure(self, mock_openai_class):
        """Test initialization fails when client creation raises exception."""
        mock_openai_class.side_effect = Exception("Client creation failed")

        with pytest.raises(
            ConfigurationError, match="Failed to initialize OVH AI client"
        ):
            OVHProvider(api_key="test-key", base_url="https://test.com")

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_success_single_message(self, mock_openai_class):
        """Test successful prediction with single message."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Hello from OVH AI!"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")
        response = provider.predict(request)

        assert response.message == "Hello from OVH AI!"
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=[{"role": Role.USER.value, "content": "Hello!"}],
            max_tokens=512,
        )

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_success_with_context(self, mock_openai_class):
        """Test successful prediction with conversation context."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock the response
        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = "Response with context"
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        context = [
            ContextMessage(role=Role.USER, content="Previous message"),
            ContextMessage(role=Role.ASSISTANT, content="Previous response"),
        ]
        request = InferenceRequest(
            model="gpt-4", message="Current message", context=context
        )
        response = provider.predict(request)

        assert response.message == "Response with context"
        expected_messages = [
            {"role": Role.USER.value, "content": "Previous message"},
            {"role": Role.ASSISTANT.value, "content": "Previous response"},
            {"role": Role.USER.value, "content": "Current message"},
        ]
        mock_client.chat.completions.create.assert_called_once_with(
            model="gpt-4",
            messages=expected_messages,
            max_tokens=512,
        )

    def test_predict_missing_model(self):
        """Test prediction fails with missing model."""
        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="", message="Hello!")

        with pytest.raises(InferenceRequestError, match="Model name is required"):
            provider.predict(request)

    def test_predict_missing_message(self):
        """Test prediction fails with missing message."""
        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="")

        with pytest.raises(InferenceRequestError, match="Message is required"):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_invalid_response(self, mock_openai_class):
        """Test prediction fails with invalid response from service."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_response.choices = []
        mock_client.chat.completions.create.return_value = mock_response

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(
            InferenceRequestError, match="Invalid response from OVH AI service"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_empty_response_message(self, mock_openai_class):
        """Test prediction fails with empty response message."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_response = Mock()
        mock_choice = Mock()
        mock_message = Mock()
        mock_message.content = ""
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(
            InferenceRequestError, match="Empty response from OVH AI service"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_authentication_error(self, mock_openai_class):
        """Test prediction handles authentication error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = openai.AuthenticationError(
            message="Invalid key",
            response=Mock(status_code=401),
            body=None,
        )

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(ConfigurationError, match="Invalid API key"):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_rate_limit_error(self, mock_openai_class):
        """Test prediction handles rate limit error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = openai.RateLimitError(
            message="Rate limited",
            response=Mock(status_code=429),
            body=None,
        )

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(InferenceRequestError, match="Rate limit exceeded"):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_not_found_error(self, mock_openai_class):
        """Test prediction handles model not found error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = openai.NotFoundError(
            message="Model not found",
            response=Mock(status_code=404),
            body=None,
        )

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="invalid-model", message="Hello!")

        with pytest.raises(
            InferenceRequestError, match="Model 'invalid-model' not found"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_timeout_error(self, mock_openai_class):
        """Test prediction handles timeout error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = openai.APITimeoutError(
            "Timeout"
        )

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(InferenceTimeoutError, match="OVH AI request timed out"):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_predict_connection_error(self, mock_openai_class):
        """Test prediction handles connection error."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_client.chat.completions.create.side_effect = openai.APIConnectionError(
            request=Mock()
        )

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        request = InferenceRequest(model="gpt-4", message="Hello!")

        with pytest.raises(
            InferenceRequestError, match="Failed to connect to OVH AI service"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_supported_models_success(self, mock_openai_class):
        """Test successful retrieval of supported models."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        # Mock models response
        mock_model1 = Mock()
        mock_model1.id = "gpt-4"
        mock_model2 = Mock()
        mock_model2.id = "gpt-3.5-turbo"
        mock_models_response = Mock()
        mock_models_response.data = [mock_model1, mock_model2]
        mock_client.models.list.return_value = mock_models_response

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")
        models = provider.supported_models()

        assert models == ["gpt-4", "gpt-3.5-turbo"]
        mock_client.models.list.assert_called_once()

    @patch("inference_client.providers.ovh.ovh_provider.OpenAI")
    def test_supported_models_failure(self, mock_openai_class):
        """Test failure when retrieving supported models."""
        mock_client = Mock()
        mock_openai_class.return_value = mock_client

        mock_client.models.list.side_effect = Exception("API error")

        provider = OVHProvider(api_key="test-key", base_url="https://test.com")

        with pytest.raises(
            InferenceRequestError, match="Failed to retrieve models from OVH AI"
        ):
            provider.supported_models()
