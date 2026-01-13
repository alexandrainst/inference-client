from enum import Enum
from typing import List, Optional


class InferenceResponse:
    """
    A response from an inference provider, containing either a message,
    images, or both.
    """

    def __init__(
        self, message: Optional[str] = None, images: Optional[List[bytes]] = None
    ):
        """
        Constructor for InferenceResponse. Creates an instance of InferenceResponse
        that holds the response message and a list of images in bytes format. Both
        fields are optional and default to None, but one of them must be provided
        to create a valid response.

        :param message: The text message returned by the inference provider.
        :type message: Optional[str]
        :param images: The images returned by the inference provider in bytes format.
        :type images: Optional[List[bytes]]
        """
        self.message = message or ""
        self.images = images or []

    def is_valid(self) -> bool:
        """
        Validate the InferenceResponse instance.

        An InferenceResponse is considered valid if it contains either a non-empty
        message or a non-empty list of images.

        :return: True if the response is valid, False otherwise.
        :rtype: bool
        """
        return bool(self.message or self.images)


class Role(str, Enum):
    """Valid roles for context messages."""

    USER = "user"
    ASSISTANT = "assistant"


class ContextMessage:
    """
    A single message in the conversation context with an explicit role.
    """

    def __init__(self, role: Role, content: str):
        """
        Constructor for ContextMessage.

        :param role: The role of the message sender.
        :type role: Role
        :param content: The content of the message.
        :type content: str
        """
        if role not in (Role.USER, Role.ASSISTANT):
            raise ValueError(f"Role must be 'user' or 'assistant', got '{role}'")
        self.role = role
        self.content = content


class InferenceRequest:
    """
    A request made to an inference provider, containing the model name,
    the input message, and optional context information.
    """

    def __init__(
        self, model: str, message: str, context: Optional[List[ContextMessage]] = None
    ):
        """
        Constructor for InferenceRequest.

        :param model: The name of the model to use for inference.
        :type model: str
        :param message: The input message to send to the model.
        :type message: str
        :param context: Optional list of previous messages in the conversation,
                        each with an explicit role ('user' or 'assistant').
        :type context: Optional[List[ContextMessage]]
        """
        self.model = model
        self.message = message
        self.context = context or []
