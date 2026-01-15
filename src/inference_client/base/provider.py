from inference_client.base.types import InferenceRequest, InferenceResponse


class BaseProvider:
    """
    Base class for all inference providers.

    This class establishes a common interface for all inference providers,
    ensuring that they implement the required methods for making inference
    requests and handling responses.
    """

    def __init__(self):
        self._models: list[str] = []

    @property
    def models(self) -> list[str]:
        """
        Get the list of supported models by this provider.

        Returns:
            A list of supported model names.
        Raises:
            InferenceRequestError: If there is an error retrieving the supported models.
        """
        if not self._models:
            self._models = self.supported_models()
        return self._models

    @models.setter
    def models(self, value: list[str]) -> None:
        """
        Set the list of supported models for this provider.

        This is useful for providers like Azure OpenAI where the list of
        available deployments cannot be retrieved via API and must be
        configured manually.

        Args:
            value: A list of model/deployment names.
        """
        self._models = value

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        Make a prediction using the inference provider.

        This method must be implemented by all subclasses to perform
        the actual inference operation.

        The exceptions mentioned below should be raised as appropriate
        by the subclasses when errors occur. E.g. if there is a configuration
        issue with the underlying provider, a ConfigurationError should be raised,
        and similarly for request and response errors. Only valid Infere

        :param request: The inference request containing model and input data.
        :type request: InferenceRequest

        Returns:
            The result of the prediction.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
            ConfigurationError: If there is a configuration issue with the underlying provider.
            InferenceRequestError: If there is an error with the inference request.
            InferenceResponseError: If there is an error with the inference response.
        """
        raise NotImplementedError("Subclasses must implement this method.")

    def supported_models(self) -> list[str]:
        """
        Return a list of supported model names by this provider.

        This method must be implemented by subclasses to provide
        specific information about the models they support. Models
        must be stored in the `_models` attribute.

        Returns:
            A list of supported model names.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
            InferenceRequestError: If there is an error retrieving the supported models.
        """
        raise NotImplementedError("Subclasses must implement this method.")
