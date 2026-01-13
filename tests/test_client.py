# tests/test_client.py

import pytest

from inference_client import (
    InferenceClient,
    InferenceRequest,
    InferenceRequestError,
    InferenceResponse,
)
from inference_client.base.provider import BaseProvider


class DummyProvider(BaseProvider):
    def predict(self, request: InferenceRequest) -> InferenceResponse:
        return InferenceResponse(message="dummy response")

    def supported_models(self) -> list[str]:
        return ["dummy"]


@pytest.fixture
def client():
    return InferenceClient(DummyProvider())


def test_inference_client_initialization(client):
    assert client is not None


def test_inference_with_empty_input(client):
    with pytest.raises(InferenceRequestError):  # Expecting an exception for empty input
        client.predict(InferenceRequest(model="dummy", message=""))


def test_inference_with_valid_input(client):
    request = InferenceRequest(model="dummy", message="Hello, world!")
    response = client.predict(request)
    assert isinstance(response, InferenceResponse)
    assert response.message == "dummy response"
