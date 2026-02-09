from typing import Sequence

from inference_client.base.provider import BaseProvider
from inference_client.base.types import InferenceRequest, InferenceResponse


class MockProvider(BaseProvider):
    """
    Mock provider useful for testing.
    """

    def __init__(self, models: Sequence[str]):
        super().__init__()
        self._models = [m for m in models]

    def supported_models(self) -> list[str]:
        return self._models

    def predict(self, request: InferenceRequest) -> InferenceResponse:
        """
        The mock predict method echoes the query back.
        """
        return InferenceResponse(message=request.message)
