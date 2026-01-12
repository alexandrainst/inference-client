from inference_client.base.types import InferenceRequest, InferenceResponse


class BaseProvider:
    """
    Base class for all inference providers.

    This class establishes a common interface for all inference providers,
    ensuring that they implement the required methods for making inference
    requests and handling responses.
    """

    def __init__(self):
        pass

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
