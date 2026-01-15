"""
This file initializes the inference_client package.
"""

from .base.types import ContextMessage, InferenceRequest, InferenceResponse
from .client import InferenceClient
from .exceptions import (
    ConfigurationError,
    InferenceClientError,
    InferenceRequestError,
    InferenceResponseError,
)

try:
    from ._version import version as __version__
except ImportError:
    # Fallback for development installations without setuptools-scm
    __version__ = "unknown"

__all__ = [
    "ContextMessage",
    "InferenceClient",
    "InferenceClientError",
    "InferenceRequestError",
    "InferenceResponseError",
    "ConfigurationError",
    "InferenceRequest",
    "InferenceResponse",
    "__version__",
]
