import os
from typing import Optional

import openai
from openai import OpenAI

from inference_client.base.provider import BaseProvider
from inference_client.base.types import InferenceRequest, InferenceResponse, Role
from inference_client.exceptions import (
    ConfigurationError,
    InferenceRequestError,
    InferenceTimeoutError,
)


class OpenAIProvider(BaseProvider):
    """
    OpenAI inference provider implementation.

    Provides cloud-based AI inference through OpenAI with support for chat-based
    interactions and model management.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize the OpenAI provider.

        :param api_key: The OpenAI API key for authentication. If not provided,
                        will read from OPENAI_API_KEY environment variable.
        :type api_key: Optional[str]
        :param base_url: Optional custom base URL for OpenAI-compatible APIs.
        :type base_url: Optional[str]
        :param timeout: Request timeout in seconds (default: 60).
        :type timeout: int

        :raises ConfigurationError: If the API key is missing or configuration is invalid.
        """
        super().__init__()

        # Use provided api_key or fall back to environment variable
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.base_url = base_url
        self.timeout = timeout

        # Validate configuration
        self._validate_configuration()

        # Initialize OpenAI client
        try:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize OpenAI client: {str(e)}")

    def _validate_configuration(self) -> None:
        """Validate configuration parameters."""
        if not self.api_key or not isinstance(self.api_key, str):
            raise ConfigurationError(
                "API key is required. Please provide a valid OpenAI API key "
                "or set the OPENAI_API_KEY environment variable."
            )

        if not self.api_key.strip():
            raise ConfigurationError(
                "API key cannot be empty. Please provide a valid OpenAI API key "
                "or set the OPENAI_API_KEY environment variable."
            )

        if self.base_url is not None:
            if not isinstance(self.base_url, str) or not self.base_url.strip():
                raise ConfigurationError("Base URL must be a non-empty string")

            if not self.base_url.startswith(("http://", "https://")):
                raise ConfigurationError("Base URL must start with http:// or https://")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ConfigurationError("Timeout must be a positive integer")

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the OpenAI inference provider.

        :param request: The inference request containing model, input data, and possibly context information.
        :type request: InferenceRequest

        :return: The inference response from OpenAI.
        :rtype: InferenceResponse

        :raises ConfigurationError: If there is a configuration issue with the OpenAI provider.
        :raises InferenceRequestError: If there is an error with the inference request.
        :raises InferenceTimeoutError: If the request times out.
        """
        # Validate request
        if not request.model:
            raise InferenceRequestError("Model name is required")

        if not request.message:
            raise InferenceRequestError("Message is required")

        try:
            # Build chat messages for OpenAI
            messages = []

            # Add context messages if provided (multi-turn conversation)
            if request.context:
                for context_msg in request.context:
                    messages.append(
                        {"role": context_msg.role.value, "content": context_msg.content}
                    )

            # Add current message
            messages.append({"role": Role.USER.value, "content": request.message})

            # Make the chat completion request
            response = self._client.chat.completions.create(
                model=request.model,
                messages=messages,
            )

            if not response or not response.choices:
                raise InferenceRequestError("Invalid response from OpenAI service")

            # Extract the assistant's message
            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                raise InferenceRequestError("Empty response from OpenAI service")

            return InferenceResponse(message=choice.message.content)

        except openai.AuthenticationError as e:
            raise ConfigurationError(
                f"Invalid API key. Please check your OpenAI API key: {str(e)}"
            )

        except openai.RateLimitError as e:
            raise InferenceRequestError(
                f"Rate limit exceeded. Please wait and try again: {str(e)}"
            )

        except openai.NotFoundError as e:
            raise InferenceRequestError(
                f"Model '{request.model}' not found. "
                f"Please check the model name or use a valid model like 'gpt-4' or 'gpt-3.5-turbo': {str(e)}"
            )

        except openai.APITimeoutError as e:
            raise InferenceTimeoutError(
                f"Request timed out after {self.timeout} seconds. "
                f"Consider increasing timeout or simplifying the request: {str(e)}"
            )

        except openai.APIConnectionError as e:
            raise InferenceRequestError(
                f"Failed to connect to OpenAI service. "
                f"Please check your network connection and try again: {str(e)}"
            )

        except openai.APIStatusError as e:
            raise InferenceRequestError(
                f"OpenAI API error (status {e.status_code}): {str(e)}. "
                f"Check OpenAI status page for service issues."
            )

        except Exception as e:
            if isinstance(
                e,
                (ConfigurationError, InferenceRequestError, InferenceTimeoutError),
            ):
                raise
            raise InferenceRequestError(
                f"Unexpected error during prediction: {str(e)}"
            )

    def supported_models(self) -> list[str]:
        """
        Return a list of supported model names by the OpenAI provider.

        :return: A list of supported model names.
        :rtype: list[str]

        :raises InferenceRequestError: If unable to retrieve models from OpenAI service.
        """
        try:
            # Get list of models from OpenAI
            models_response = self._client.models.list()

            if not models_response:
                raise InferenceRequestError(
                    "Invalid response when fetching models from OpenAI"
                )

            # Extract model IDs
            model_ids = [model.id for model in models_response.data]

            if not model_ids:
                raise InferenceRequestError("No models available from OpenAI API")

            return model_ids

        except openai.AuthenticationError as e:
            raise ConfigurationError(
                f"Invalid API key. Please check your OpenAI API key: {str(e)}"
            )

        except Exception as e:
            if isinstance(e, (ConfigurationError, InferenceRequestError)):
                raise
            raise InferenceRequestError(
                f"Failed to retrieve supported models: {str(e)}"
            )
