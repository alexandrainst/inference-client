class InferenceClientError(Exception):
    """Base class for exceptions in the Inference Client library."""

    pass


class InferenceRequestError(InferenceClientError):
    """Exception raised for errors during inference requests."""

    def __init__(self, message: str):
        super().__init__(message)


class InferenceResponseError(InferenceClientError):
    """Exception raised for errors in inference responses."""

    def __init__(self, message: str):
        super().__init__(message)


class ConfigurationError(InferenceClientError):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str):
        super().__init__(message)
