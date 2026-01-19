"""
OVH AI inference provider implementation.

This provider uses OVH's hosted AI service, which is OpenAI-compatible.
OVH AI provides European-hosted inference with GDPR compliance.

This requires:
- An OVH API key
- An OVH AI endpoint URL
- A model name from available OVH AI models
"""

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


class OVHProvider(BaseProvider):
    """
    OVH AI inference provider implementation.

    Provides cloud-based AI inference through OVH AI with support for
    chat-based interactions and model management.

    OVH AI is OpenAI-compatible, so it uses standard model names
    like "gpt-4", "gpt-3.5-turbo", etc.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = 60,
    ):
        """
        Initialize the OVH AI provider.

        :param api_key: The OVH API key for authentication. If not provided,
                        will read from OVH_API_KEY environment variable.
        :type api_key: Optional[str]
        :param base_url: The OVH AI base URL.
                      If not provided, will read from OVH_AI_ENDPOINT environment variable.
        :type base_url: Optional[str]
        :param timeout: Request timeout in seconds (default: 60).
        :type timeout: int

        :raises ConfigurationError: If required configuration is missing or invalid.
        """
        super().__init__()

        # Use provided values or fall back to environment variables
        self.api_key = api_key if api_key is not None else os.environ.get("OVH_API_KEY")
        self.base_url = (
            base_url if base_url is not None else os.environ.get("OVH_AI_ENDPOINT")
        )
        self.timeout = timeout

        # Validate configuration
        self._validate_configuration()

        # Initialize OpenAI client with OVH endpoint
        try:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize OVH AI client: {str(e)}")

    def _validate_configuration(self) -> None:
        """Validate configuration parameters."""
        if self.api_key is None or not isinstance(self.api_key, str):
            raise ConfigurationError(
                "API key is required. Please provide a valid OVH AI API key "
                "or set the OVH_API_KEY environment variable."
            )

        if not self.api_key.strip():
            raise ConfigurationError(
                "API key cannot be empty. Please provide a valid OVH AI API key "
                "or set the OVH_API_KEY environment variable."
            )

        if self.base_url is None or not isinstance(self.base_url, str):
            raise ConfigurationError(
                "Base URL is required. Please provide the OVH AI endpoint URL "
                "or set the OVH_AI_ENDPOINT environment variable."
            )

        if not self.base_url.strip():
            raise ConfigurationError(
                "Base URL cannot be empty. Please provide the OVH AI endpoint URL "
                "or set the OVH_AI_ENDPOINT environment variable."
            )

        if not self.base_url.startswith("https://"):
            raise ConfigurationError("Base URL must start with https://.")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ConfigurationError("Timeout must be a positive integer")

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the OVH AI inference provider.

        :param request: The inference request containing model name and input data.
        :type request: InferenceRequest

        :return: The inference response from OVH AI.
        :rtype: InferenceResponse

        :raises ConfigurationError: If there is a configuration issue.
        :raises InferenceRequestError: If there is an error with the inference request.
        :raises InferenceTimeoutError: If the request times out.
        """
        # Validate request
        if not request.model:
            raise InferenceRequestError(
                "Model name is required. Please specify a valid OVH AI model name."
            )

        if not request.message:
            raise InferenceRequestError("Message is required")

        try:
            # Build chat messages
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
                max_tokens=512,
            )

            if not response or not response.choices:
                raise InferenceRequestError("Invalid response from OVH AI service")

            # Extract the assistant's message
            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                raise InferenceRequestError("Empty response from OVH AI service")

            return InferenceResponse(message=choice.message.content)

        except openai.AuthenticationError as e:
            raise ConfigurationError(
                f"Invalid API key. Please check your OVH API key: {str(e)}"
            )

        except openai.RateLimitError as e:
            raise InferenceRequestError(
                f"Rate limit exceeded. Please wait and try again: {str(e)}"
            )

        except openai.NotFoundError as e:
            raise InferenceRequestError(
                f"Model '{request.model}' not found. "
                f"Please verify the model is available in OVH AI: {str(e)}"
            )

        except openai.BadRequestError as e:
            raise InferenceRequestError(f"Invalid request to OVH AI: {str(e)}")

        except openai.APITimeoutError as e:
            raise InferenceTimeoutError(
                f"OVH AI request timed out after {self.timeout}s: {str(e)}"
            )

        except openai.APIConnectionError as e:
            raise InferenceRequestError(
                f"Failed to connect to OVH AI service: {str(e)}"
            )

        except openai.APIError as e:
            raise InferenceRequestError(f"OVH AI API error: {str(e)}")

    def supported_models(self) -> list[str]:
        """
        Return list of available models from OVH AI.

        :return: List of available model names.
        :rtype: list[str]

        :raises InferenceRequestError: If there is an error retrieving the models.
        """
        try:
            models_response = self._client.models.list()
            return [model.id for model in models_response.data]
        except Exception as e:
            raise InferenceRequestError(
                f"Failed to retrieve models from OVH AI: {str(e)}"
            )
