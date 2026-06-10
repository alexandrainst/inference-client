"""
Generic OpenAI-compatible inference provider implementation.

Any inference server that speaks the OpenAI chat-completions protocol can be
driven through this provider by supplying an API key, a base URL and a model
name. Vendor-specific providers (e.g. OVH) subclass this and only customise
naming and environment-variable fallbacks.
"""

import os

import openai
from openai import OpenAI

from inference_client.base.provider import BaseProvider
from inference_client.base.types import InferenceRequest, InferenceResponse, Role
from inference_client.exceptions import (
    ConfigurationError,
    InferenceRequestError,
    InferenceTimeoutError,
)


class OpenAICompatibleProvider(BaseProvider):
    """
    Inference provider for any OpenAI-compatible chat-completions endpoint.

    The endpoint is identified purely by ``base_url`` + ``api_key``; model
    names are whatever the server advertises via ``/v1/models``. Subclasses
    may set ``provider_name`` (used in error messages) and the
    ``api_key_env`` / ``base_url_env`` fallbacks.
    """

    #: Human-readable name used in error messages.
    provider_name: str = "OpenAI-compatible server"
    #: Environment variable read when ``api_key`` is not passed explicitly.
    api_key_env: str | None = None
    #: Environment variable read when ``base_url`` is not passed explicitly.
    base_url_env: str | None = None
    #: When True, the base URL must use https:// (set by vendors that mandate
    #: TLS, e.g. OVH). Generic self-hosted servers may run over plain http.
    require_https: bool = False

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: int = 60,
    ):
        """
        Initialize the OpenAI-compatible provider.

        :param api_key: API key for authentication. Falls back to the
                        ``api_key_env`` environment variable when not provided.
        :type api_key: str | None
        :param base_url: Base URL of the endpoint (e.g.
                         ``https://host/v1``). Falls back to ``base_url_env``.
        :type base_url: str | None
        :param timeout: Request timeout in seconds (default: 60).
        :type timeout: int

        :raises ConfigurationError: If required configuration is missing or invalid.
        """
        super().__init__()

        # Use provided values or fall back to environment variables.
        if api_key is None and self.api_key_env:
            api_key = os.environ.get(self.api_key_env)
        if base_url is None and self.base_url_env:
            base_url = os.environ.get(self.base_url_env)

        self.api_key = api_key
        self.base_url = base_url
        self.timeout = timeout

        self._validate_configuration()

        try:
            self._client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                timeout=self.timeout,
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize {self.provider_name} client: {str(e)}"
            )

    def _validate_configuration(self) -> None:
        """Validate configuration parameters."""
        if self.api_key is None or not isinstance(self.api_key, str):
            raise ConfigurationError(
                f"API key is required. Please provide a valid {self.provider_name} "
                "API key"
                + (f" or set the {self.api_key_env} environment variable." if self.api_key_env else ".")
            )

        if not self.api_key.strip():
            raise ConfigurationError(
                f"API key cannot be empty. Please provide a valid {self.provider_name} "
                "API key"
                + (f" or set the {self.api_key_env} environment variable." if self.api_key_env else ".")
            )

        if self.base_url is None or not isinstance(self.base_url, str):
            raise ConfigurationError(
                f"Base URL is required. Please provide the {self.provider_name} "
                "endpoint URL"
                + (f" or set the {self.base_url_env} environment variable." if self.base_url_env else ".")
            )

        if not self.base_url.strip():
            raise ConfigurationError(
                f"Base URL cannot be empty. Please provide the {self.provider_name} "
                "endpoint URL"
                + (f" or set the {self.base_url_env} environment variable." if self.base_url_env else ".")
            )

        if self.require_https:
            if not self.base_url.startswith("https://"):
                raise ConfigurationError("Base URL must start with https://.")
        elif not self.base_url.startswith(("http://", "https://")):
            raise ConfigurationError("Base URL must start with http:// or https://.")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ConfigurationError("Timeout must be a positive integer")

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the OpenAI-compatible inference provider.

        :param request: The inference request containing model name and input data.
        :type request: InferenceRequest

        :return: The inference response from the server.
        :rtype: InferenceResponse

        :raises ConfigurationError: If there is a configuration issue.
        :raises InferenceRequestError: If there is an error with the inference request.
        :raises InferenceTimeoutError: If the request times out.
        """
        if not request.model:
            raise InferenceRequestError(
                f"Model name is required. Please specify a valid {self.provider_name} "
                "model name."
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
            )

            if not response or not response.choices:
                raise InferenceRequestError(
                    f"Invalid response from {self.provider_name}"
                )

            # Extract the assistant's message
            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                raise InferenceRequestError(
                    f"Empty response from {self.provider_name}"
                )

            return InferenceResponse(message=choice.message.content)

        except openai.AuthenticationError as e:
            raise ConfigurationError(
                f"Invalid API key. Please check your {self.provider_name} API key: {str(e)}"
            )

        except openai.RateLimitError as e:
            raise InferenceRequestError(
                f"Rate limit exceeded. Please wait and try again: {str(e)}"
            )

        except openai.NotFoundError as e:
            raise InferenceRequestError(
                f"Model '{request.model}' not found. "
                f"Please verify the model is available on {self.provider_name}: {str(e)}"
            )

        except openai.BadRequestError as e:
            raise InferenceRequestError(
                f"Invalid request to {self.provider_name}: {str(e)}"
            )

        except openai.APITimeoutError as e:
            raise InferenceTimeoutError(
                f"{self.provider_name} request timed out after {self.timeout}s: {str(e)}"
            )

        except openai.APIConnectionError as e:
            raise InferenceRequestError(
                f"Failed to connect to {self.provider_name}: {str(e)}"
            )

        except openai.APIError as e:
            raise InferenceRequestError(f"{self.provider_name} API error: {str(e)}")

    def supported_models(self) -> list[str]:
        """
        Return list of available models advertised by the endpoint.

        :return: List of available model names.
        :rtype: list[str]

        :raises InferenceRequestError: If there is an error retrieving the models.
        """
        try:
            models_response = self._client.models.list()
            return [model.id for model in models_response.data]
        except Exception as e:
            raise InferenceRequestError(
                f"Failed to retrieve models from {self.provider_name}: {str(e)}"
            )
