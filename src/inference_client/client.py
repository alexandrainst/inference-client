from typing import Optional

from inference_client.base.provider import BaseProvider
from inference_client.base.types import InferenceRequest, InferenceResponse
from inference_client.exceptions import InferenceRequestError
from inference_client.providers.azure_openai import AzureOpenAIProvider
from inference_client.providers.ollama import OllamaProvider


class InferenceClient:
    def __init__(self, provider: BaseProvider):
        self.provider = provider

    @classmethod
    def create_ollama_client(
        cls, host: str, api_key: Optional[str] = None
    ) -> "InferenceClient":
        """
        Create an InferenceClient instance configured to use the Ollama provider.

        :param host: The host URL for the Ollama provider.
        :param api_key: The optional API key for Ollama.

        :return: An InferenceClient instance with OllamaProvider.
        :rtype: InferenceClient
        """
        ollama_provider = OllamaProvider(host, api_key)
        return cls(provider=ollama_provider)

    @classmethod
    def create_azure_openai_client(
        cls,
        api_key: Optional[str] = None,
        azure_endpoint: Optional[str] = None,
        api_version: str = "2024-02-01",
        timeout: int = 60,
        deployments: Optional[list[str]] = None,
    ) -> "InferenceClient":
        """
        Create an InferenceClient instance configured to use the Azure OpenAI provider.

        :param api_key: The Azure OpenAI API key. If not provided,
                        reads from AZURE_OPENAI_API_KEY environment variable.
        :type api_key: Optional[str]
        :param azure_endpoint: The Azure OpenAI resource endpoint URL.
                               Example: https://your-resource-name.openai.azure.com
                               If not provided, reads from AZURE_OPENAI_ENDPOINT.
        :type azure_endpoint: Optional[str]
        :param api_version: The Azure OpenAI API version (default: "2024-02-01").
        :type api_version: str
        :param timeout: Request timeout in seconds (default: 60).
        :type timeout: int
        :param deployments: List of deployment names available in your Azure OpenAI resource.
                            Required for model validation. These are the names you created
                            in the Azure portal, not the underlying model names.
        :type deployments: Optional[list[str]]

        :return: An InferenceClient instance with AzureOpenAIProvider.
        :rtype: InferenceClient

        :raises ConfigurationError: If required configuration is missing.

        Example::

            client = create_azure_openai_client(
                deployments=["my-gpt4-deployment", "my-gpt35-deployment"]
            )
            response = client.predict(InferenceRequest(
                model="my-gpt4-deployment",
                message="Hello!"
            ))
        """
        provider = AzureOpenAIProvider(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            timeout=timeout,
        )

        # Set the deployments list so model validation works
        if deployments:
            provider.models = deployments

        return cls(provider=provider)

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the configured inference provider.
        The request only accepts text input and a context for now, but
        the response can contain both text and images.

        :param self: Description
        :param request: Description
        :type request: InferenceRequest
        :return: Description
        :rtype: InferenceResponse
        """
        # Sanity check - don't allow empty messages
        if not request.message.strip():
            raise InferenceRequestError("Input message cannot be empty.")

        if request.model not in self.provider.models:
            raise InferenceRequestError(
                f"Model '{request.model}' is not supported by the provider."
            )

        response = self.provider.predict(request)
        return response

    def models(self) -> list[str]:
        """
        Get the list of supported models from the configured provider.

        :return: A list of supported model names.
        :rtype: list[str]
        """
        return self.provider.models
