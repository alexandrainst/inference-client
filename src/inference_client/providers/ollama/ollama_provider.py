import os
from typing import Optional

import ollama
from ollama import Client

from inference_client.base.provider import BaseProvider
from inference_client.base.types import InferenceRequest, InferenceResponse, Role
from inference_client.exceptions import (
    ConfigurationError,
    InferenceRequestError,
    InferenceTimeoutError,
)


class OllamaProvider(BaseProvider):
    """
    Ollama inference provider implementation.

    Provides local AI inference through Ollama with support for chat-based
    interactions and model management.
    """

    def __init__(
        self,
        host: str = "http://localhost:11434",
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        super().__init__()

        # The Ollama Python library reads the api_key from environment variables,
        # if we get an api_key, we set it here.
        if api_key:
            os.environ["OLLAMA_API_KEY"] = api_key

        self.host = host
        self.timeout = timeout

        # Validate configuration
        self._validate_configuration()

        # Initialize Ollama clients
        try:
            self._client = Client(host=self.host)
        except Exception as e:
            raise ConfigurationError(f"Failed to initialize Ollama client: {str(e)}")

    def _validate_configuration(self) -> None:
        """Validate configuration parameters."""
        if not isinstance(self.host, str) or not self.host.strip():
            raise ConfigurationError("Host must be a non-empty string")

        if not self.host.startswith(("http://", "https://")):
            raise ConfigurationError("Host must start with http:// or https://")

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ConfigurationError("Timeout must be a positive integer")

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the Ollama inference provider.

        :param request: The inference request containing model, input data, and possibly context information.
        :type request: InferenceRequest

        :return: The inference response from Ollama.
        :rtype: InferenceResponse

        :raises ConfigurationError: If there is a configuration issue with the Ollama provider.
        :raises InferenceRequestError: If there is an error with the inference request.
        :raises InferenceTimeoutError: If the request times out.
        """
        # Validate request
        if not request.model:
            raise InferenceRequestError("Model name is required")

        if not request.message:
            raise InferenceRequestError("Message is required")

        try:
            # Build chat messages for Ollama
            messages = []

            # Add context messages if provided (multi-turn conversation)
            if request.context:
                for context_msg in request.context:
                    messages.append(
                        {"role": context_msg.role, "content": context_msg.content}
                    )

            # Add current message
            messages.append({"role": Role.USER, "content": request.message})

            # Make the chat request
            response = self._client.chat(
                model=request.model,
                messages=messages,
                options={"timeout": self.timeout},
            )

            if not response:
                raise InferenceRequestError("Invalid response from Ollama service")

            # Extract message - handle both typed response and dict format
            message_obj = getattr(response, "message", None)
            if message_obj is None:
                message_obj = (
                    response.get("message") if isinstance(response, dict) else None
                )

            if not message_obj:
                raise InferenceRequestError("Invalid response from Ollama service")

            # Extract content from message
            assistant_message = getattr(message_obj, "content", None)
            if assistant_message is None:
                assistant_message = (
                    message_obj.get("content", "")
                    if isinstance(message_obj, dict)
                    else ""
                )

            if not assistant_message:
                raise InferenceRequestError("Empty response from Ollama service")

            return InferenceResponse(message=assistant_message)

        except ollama.ResponseError as e:
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise InferenceRequestError(
                    f"Model '{request.model}' not found. "
                    f"Please pull the model using: ollama pull {request.model}"
                )
            else:
                raise InferenceRequestError(f"Ollama service error: {str(e)}")

        except Exception as e:
            if "timeout" in str(e).lower():
                raise InferenceTimeoutError(
                    f"Request timed out after {self.timeout} seconds. "
                    f"Consider increasing timeout or using a smaller model."
                )
            else:
                raise InferenceRequestError(
                    f"Unexpected error during prediction: {str(e)}"
                )

    def supported_models(self) -> list[str]:
        """
        Return a list of supported model names by the Ollama provider.

        :return: A list of supported model names.
        :rtype: list[str]

        :raises InferenceRequestError: If unable to retrieve models from Ollama service.
        """
        try:
            # Get list of models from Ollama
            models_response = self._client.list()

            if not models_response:
                raise InferenceRequestError(
                    "Invalid response when fetching models from Ollama"
                )

            # Extract models - handle both typed response and dict format
            models = getattr(models_response, "models", None)
            if models is None:
                models = (
                    models_response.get("models", [])
                    if isinstance(models_response, dict)
                    else []
                )

            if not models:
                raise InferenceRequestError(
                    "No models available in Ollama. "
                    "Please pull at least one model using: ollama pull <model-name>"
                )

            # Extract model names - handle both Model objects and dicts
            model_names = []
            for model in models:
                name = getattr(model, "model", None) or (
                    model.get("name") if isinstance(model, dict) else None
                )
                if name:
                    model_names.append(name)

            if not model_names:
                raise InferenceRequestError(
                    "No models available in Ollama. "
                    "Please pull at least one model using: ollama pull <model-name>"
                )

            return model_names

        except Exception as e:
            if isinstance(e, InferenceRequestError):
                raise
            else:
                raise InferenceRequestError(
                    f"Failed to retrieve supported models: {str(e)}. "
                    f"Please ensure Ollama service is running at {self.host}"
                )
