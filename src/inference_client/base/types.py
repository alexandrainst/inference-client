from enum import Enum


class InferenceResponse:
    """
    A response from an inference provider, containing either a message,
    images, or both.
    """

    def __init__(
        self, message: str | None = None, images: list[bytes] | None = None
    ):
        """
        Constructor for InferenceResponse. Creates an instance of InferenceResponse
        that holds the response message and a list of images in bytes format. Both
        fields are optional and default to None, but one of them must be provided
        to create a valid response.

        :param message: The text message returned by the inference provider.
        :type message: str | None
        :param images: The images returned by the inference provider in bytes format.
        :type images: list[bytes] | None
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


class Role(Enum):
    """
    Roles a chat message can have.

    Only USER and ASSISTANT are valid for chat history messages; SYSTEM is set
    through ``InferenceRequest.system_prompt``.
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class ChatMessage:
    """
    A single message in the chat history with an explicit role.
    """

    def __init__(self, role: Role, content: str):
        """
        Constructor for ChatMessage.

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
    the input message, and optional chat history, images and system prompt.
    """

    def __init__(
        self,
        model: str,
        message: str,
        chat_history: list[ChatMessage] | None = None,
        images: list[bytes] | None = None,
        system_prompt: str | None = None,
    ):
        """
        Constructor for InferenceRequest.

        :param model: The name of the model to use for inference.
        :type model: str
        :param message: The input message to send to the model.
        :type message: str
        :param chat_history: Optional list of previous messages in the
                             conversation, each with an explicit role
                             ('user' or 'assistant').
        :type chat_history: list[ChatMessage] | None
        :param images: Optional list of images as raw bytes to send with the message.
        :type images: list[bytes] | None
        :param system_prompt: Optional instructions sent to the model as a
                              leading system message. Empty or whitespace-only
                              values are treated as no system prompt.
        :type system_prompt: str | None
        """
        self.model = model
        self.message = message
        self.chat_history = chat_history or []
        self.images = images or []
        self.system_prompt = system_prompt
