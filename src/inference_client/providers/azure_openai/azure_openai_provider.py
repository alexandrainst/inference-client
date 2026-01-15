"""
Azure OpenAI inference provider implementation.

This provider uses Azure's hosted OpenAI service, which requires:
- An Azure OpenAI resource endpoint
- An API key or Azure AD authentication
- A deployment name (not model name)
"""

import os
from typing import Optional

import openai
from openai import AzureOpenAI

from inference_client.base.provider import BaseProvider
from inference_client.base.types import InferenceRequest, InferenceResponse, Role
from inference_client.exceptions import (
    ConfigurationError,
    InferenceRequestError,
    InferenceTimeoutError,
)


class AzureOpenAIProvider(BaseProvider):
    """
    Azure OpenAI inference provider implementation.

    Provides cloud-based AI inference through Azure OpenAI with support for
    chat-based interactions and deployment management.

    Azure OpenAI uses "deployments" instead of model names directly.
    You create a deployment in Azure portal and reference it by name.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: str = "2024-02-01",
        timeout: int = 60,
    ):
        """
        Initialize the Azure OpenAI provider.

        :param api_key: The Azure OpenAI API key for authentication. If not provided,
                        will read from AZURE_OPENAI_API_KEY environment variable.
        :type api_key: Optional[str]
        :param azure_endpoint: The Azure OpenAI resource endpoint URL.
                               Example: https://your-resource-name.openai.azure.com
                               If not provided, will read from AZURE_OPENAI_ENDPOINT
                               environment variable.
        :type azure_endpoint: Optional[str]
        :param api_version: The Azure OpenAI API version (default: "2024-02-01").
        :type api_version: str
        :param timeout: Request timeout in seconds (default: 60).
        :type timeout: int

        :raises ConfigurationError: If required configuration is missing or invalid.
        """
        super().__init__()

        # Use provided values or fall back to environment variables
        self.api_key = api_key or os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = azure_endpoint or os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.api_version = api_version
        self.timeout = timeout

        # Validate configuration
        self._validate_configuration()

        # Initialize Azure OpenAI client
        try:
            self._client = AzureOpenAI(
                api_key=self.api_key,
                azure_endpoint=self.azure_endpoint,
                api_version=self.api_version,
                timeout=self.timeout,
            )
        except Exception as e:
            raise ConfigurationError(
                f"Failed to initialize Azure OpenAI client: {str(e)}"
            )

    def _validate_configuration(self) -> None:
        """Validate configuration parameters."""
        if not self.api_key or not isinstance(self.api_key, str):
            raise ConfigurationError(
                "API key is required. Please provide a valid Azure OpenAI API key "
                "or set the AZURE_OPENAI_API_KEY environment variable."
            )

        if not self.api_key.strip():
            raise ConfigurationError(
                "API key cannot be empty. Please provide a valid Azure OpenAI API key "
                "or set the AZURE_OPENAI_API_KEY environment variable."
            )

        if not self.azure_endpoint or not isinstance(self.azure_endpoint, str):
            raise ConfigurationError(
                "Azure endpoint is required. Please provide the Azure OpenAI endpoint URL "
                "or set the AZURE_OPENAI_ENDPOINT environment variable. "
                "Example: https://your-resource-name.openai.azure.com"
            )

        if not self.azure_endpoint.strip():
            raise ConfigurationError(
                "Azure endpoint cannot be empty. Please provide the Azure OpenAI endpoint URL "
                "or set the AZURE_OPENAI_ENDPOINT environment variable."
            )

        if not self.azure_endpoint.startswith("https://"):
            raise ConfigurationError(
                "Azure endpoint must start with https://. "
                "Example: https://your-resource-name.openai.azure.com"
            )

        if not isinstance(self.timeout, int) or self.timeout <= 0:
            raise ConfigurationError("Timeout must be a positive integer")

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the Azure OpenAI inference provider.

        Note: In Azure OpenAI, the 'model' field in the request should be the
        deployment name, not the underlying model name (e.g., "my-gpt4-deployment"
        instead of "gpt-4").

        :param request: The inference request containing deployment name and input data.
        :type request: InferenceRequest

        :return: The inference response from Azure OpenAI.
        :rtype: InferenceResponse

        :raises ConfigurationError: If there is a configuration issue.
        :raises InferenceRequestError: If there is an error with the inference request.
        :raises InferenceTimeoutError: If the request times out.
        """
        # Validate request
        if not request.model:
            raise InferenceRequestError(
                "Deployment name is required. In Azure OpenAI, use the deployment "
                "name you created in the Azure portal."
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
            # In Azure OpenAI, 'model' parameter is the deployment name
            response = self._client.chat.completions.create(
                model=request.model,  # This is the deployment name in Azure
                messages=messages,
            )

            if not response or not response.choices:
                raise InferenceRequestError(
                    "Invalid response from Azure OpenAI service"
                )

            # Extract the assistant's message
            choice = response.choices[0]
            if not choice.message or not choice.message.content:
                raise InferenceRequestError(
                    "Empty response from Azure OpenAI service"
                )

            return InferenceResponse(message=choice.message.content)

        except openai.AuthenticationError as e:
            raise ConfigurationError(
                f"Invalid API key. Please check your Azure OpenAI API key: {str(e)}"
            )

        except openai.RateLimitError as e:
            raise InferenceRequestError(
                f"Rate limit exceeded. Please wait and try again: {str(e)}"
            )

        except openai.NotFoundError as e:
            raise InferenceRequestError(
                f"Deployment '{request.model}' not found. "
                f"Please verify the deployment exists in your Azure OpenAI resource: {str(e)}"
            )

        except openai.BadRequestError as e:
            raise InferenceRequestError(f"Invalid request to Azure OpenAI: {str(e)}")

        except openai.APITimeoutError as e:
            raise InferenceTimeoutError(
                f"Azure OpenAI request timed out after {self.timeout}s: {str(e)}"
            )

        except openai.APIConnectionError as e:
            raise InferenceRequestError(
                f"Failed to connect to Azure OpenAI service: {str(e)}"
            )

        except openai.APIError as e:
            raise InferenceRequestError(f"Azure OpenAI API error: {str(e)}")

    def supported_models(self) -> list[str]:
        """
        Return list of available deployments.

        Note: Azure OpenAI does not provide an API to list deployments.
        This method returns an empty list. You should know your deployment
        names from the Azure portal.

        :return: Empty list (Azure doesn't expose deployment listing via API).
        :rtype: list[str]
        """
        # Azure OpenAI doesn't have an API to list deployments
        # Users need to know their deployment names from the Azure portal
        return []
