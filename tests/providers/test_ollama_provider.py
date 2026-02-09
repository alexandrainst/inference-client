import os
from unittest.mock import Mock, patch

import ollama
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
from inference_client.providers.ollama.ollama_provider import OllamaProvider


class TestOllamaProvider:
    """Test suite for OllamaProvider."""

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_init_with_defaults(self, mock_client_class):
        """Test provider initialization with default settings."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()

        assert provider.host == "http://localhost:11434"
        assert provider.timeout == 30
        mock_client_class.assert_called_once_with(host="http://localhost:11434")

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_init_with_custom_config(self, mock_client_class):
        """Test provider initialization with custom configuration."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        provider = OllamaProvider(
            host="http://custom:8080", api_key="test_key", timeout=60
        )

        assert provider.host == "http://custom:8080"
        assert os.environ["OLLAMA_API_KEY"] == "test_key"
        assert provider.timeout == 60
        mock_client_class.assert_called_once_with(host="http://custom:8080")

    def test_init_invalid_host(self):
        """Test initialization with invalid host raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Host must start with http://"):
            OllamaProvider(host="invalid-host")

    def test_init_empty_host(self):
        """Test initialization with empty host raises ConfigurationError."""
        with pytest.raises(ConfigurationError, match="Host must be a non-empty string"):
            OllamaProvider(host="")

    def test_init_invalid_timeout(self):
        """Test initialization with invalid timeout raises ConfigurationError."""
        with pytest.raises(
            ConfigurationError, match="Timeout must be a positive integer"
        ):
            OllamaProvider(timeout=-1)

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_single_message(self, mock_client_class):
        """Test basic prediction with single message."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}
        mock_client.chat.return_value = {
            "message": {"content": "Hello! How can I help you?"}
        }

        provider = OllamaProvider()
        request = InferenceRequest(model="llama2:7b", message="Hello")

        # Execute
        response = provider.predict(request)

        # Verify
        assert isinstance(response, InferenceResponse)
        assert response.message == "Hello! How can I help you?"
        mock_client.chat.assert_called_once_with(
            model="llama2:7b",
            messages=[{"role": Role.USER, "content": "Hello"}],
            options={"timeout": 30},
        )

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_with_context(self, mock_client_class):
        """Test prediction with conversation context."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}
        mock_client.chat.return_value = {
            "message": {"content": "Python is great for data science!"}
        }

        provider = OllamaProvider()
        request = InferenceRequest(
            model="llama2:7b",
            message="What about Python?",
            context=[
                ContextMessage(
                    role=Role.USER, content="What's a good programming language?"
                ),
                ContextMessage(
                    role=Role.ASSISTANT,
                    content="JavaScript is good for web development",
                ),
            ],
        )

        # Execute
        response = provider.predict(request)

        # Verify
        expected_messages = [
            {"role": Role.USER, "content": "What's a good programming language?"},
            {
                "role": Role.ASSISTANT,
                "content": "JavaScript is good for web development",
            },
            {"role": Role.USER, "content": "What about Python?"},
        ]

        mock_client.chat.assert_called_once_with(
            model="llama2:7b", messages=expected_messages, options={"timeout": 30}
        )
        assert response.message == "Python is great for data science!"

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_with_consecutive_user_messages(self, mock_client_class):
        """Test prediction with consecutive user messages (agent mode scenario)."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}
        mock_client.chat.return_value = {
            "message": {"content": "I'll help you with both requests."}
        }

        provider = OllamaProvider()
        request = InferenceRequest(
            model="llama2:7b",
            message="And also explain generators",
            context=[
                ContextMessage(role=Role.USER, content="Explain Python decorators"),
                ContextMessage(role=Role.USER, content="Actually, wait"),
            ],
        )

        # Execute
        response = provider.predict(request)

        # Verify - consecutive user messages are preserved
        expected_messages = [
            {"role": Role.USER, "content": "Explain Python decorators"},
            {"role": Role.USER, "content": "Actually, wait"},
            {"role": Role.USER, "content": "And also explain generators"},
        ]

        mock_client.chat.assert_called_once_with(
            model="llama2:7b", messages=expected_messages, options={"timeout": 30}
        )
        assert response.message == "I'll help you with both requests."

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_with_consecutive_assistant_messages(self, mock_client_class):
        """Test prediction with consecutive assistant messages (agent mode scenario)."""
        # Setup
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}
        mock_client.chat.return_value = {
            "message": {"content": "Sure, I can continue helping."}
        }

        provider = OllamaProvider()
        request = InferenceRequest(
            model="llama2:7b",
            message="Continue",
            context=[
                ContextMessage(role=Role.USER, content="Help me debug this"),
                ContextMessage(role=Role.ASSISTANT, content="Let me check the code..."),
                ContextMessage(role=Role.ASSISTANT, content="I found the issue!"),
            ],
        )

        # Execute
        response = provider.predict(request)

        # Verify - consecutive assistant messages are preserved
        expected_messages = [
            {"role": Role.USER, "content": "Help me debug this"},
            {"role": Role.ASSISTANT, "content": "Let me check the code..."},
            {"role": Role.ASSISTANT, "content": "I found the issue!"},
            {"role": Role.USER, "content": "Continue"},
        ]

        mock_client.chat.assert_called_once_with(
            model="llama2:7b", messages=expected_messages, options={"timeout": 30}
        )
        assert response.message == "Sure, I can continue helping."

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_empty_model(self, mock_client_class):
        """Test prediction with empty model raises InferenceRequestError."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        request = InferenceRequest(model="", message="Hello")

        with pytest.raises(InferenceRequestError, match="Model name is required"):
            provider.predict(request)

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_empty_message(self, mock_client_class):
        """Test prediction with empty message raises InferenceRequestError."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        provider = OllamaProvider()
        request = InferenceRequest(model="llama2:7b", message="")

        with pytest.raises(InferenceRequestError, match="Message is required"):
            provider.predict(request)

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_model_not_found(self, mock_client_class):
        """Test prediction with non-existent model."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}
        mock_client.chat.side_effect = ollama.ResponseError("model not found")

        provider = OllamaProvider()
        request = InferenceRequest(model="nonexistent", message="Hello")

        with pytest.raises(
            InferenceRequestError, match="Model 'nonexistent' not found"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_timeout_error(self, mock_client_class):
        """Test prediction timeout handling."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}
        mock_client.chat.side_effect = Exception("Request timeout")

        provider = OllamaProvider()
        request = InferenceRequest(model="llama2:7b", message="Hello")

        with pytest.raises(
            InferenceTimeoutError, match="Request timed out after 30 seconds"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_predict_connection_error(self, mock_client_class):
        """Test prediction with connection error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.chat.side_effect = Exception("Connection refused")

        provider = OllamaProvider()
        request = InferenceRequest(model="llama2:7b", message="Hello")

        with pytest.raises(
            InferenceRequestError, match="Unexpected error during prediction.*"
        ):
            provider.predict(request)

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_supported_models_success(self, mock_client_class):
        """Test successful retrieval of supported models."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {
            "models": [
                {"name": "llama2:7b"},
                {"name": "mistral:7b"},
                {"name": "codellama:13b"},
            ]
        }

        provider = OllamaProvider()
        models = provider.supported_models()

        assert models == ["llama2:7b", "mistral:7b", "codellama:13b"]

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_supported_models_empty_list(self, mock_client_class):
        """Test supported_models with no available models."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {"models": []}

        provider = OllamaProvider()
        models = provider.supported_models()
        assert len(models) == 0

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_supported_models_connection_error(self, mock_client_class):
        """Test supported_models with connection error."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.side_effect = Exception("Connection refused")

        provider = OllamaProvider()

        with pytest.raises(
            InferenceRequestError, match="Failed to retrieve supported models.*"
        ):
            provider.supported_models()

    @patch("inference_client.providers.ollama.ollama_provider.Client")
    def test_supported_models_invalid_response(self, mock_client_class):
        """Test supported_models with invalid response."""
        mock_client = Mock()
        mock_client_class.return_value = mock_client
        mock_client.list.return_value = {}  # Missing 'models' key

        provider = OllamaProvider()

        with pytest.raises(
            InferenceRequestError, match="Invalid response when fetching models"
        ):
            provider.supported_models()
