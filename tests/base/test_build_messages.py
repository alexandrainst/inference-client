import pytest

from inference_client.base.provider import BaseProvider
from inference_client.base.types import ContextMessage, InferenceRequest, Role


class TestBuildMessages:
    """Tests for the chat message list shared by all providers."""

    def test_without_system_prompt(self):
        """Test that no system message is added when system_prompt is None."""
        request = InferenceRequest(model="m", message="Hello")

        assert BaseProvider._build_messages(request) == [
            {"role": "user", "content": "Hello"}
        ]

    def test_with_system_prompt(self):
        """Test that the system prompt becomes the first message."""
        request = InferenceRequest(
            model="m", message="Hello", system_prompt="Be concise."
        )

        assert BaseProvider._build_messages(request) == [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hello"},
        ]

    @pytest.mark.parametrize("system_prompt", ["", "   ", "\n\t"])
    def test_empty_system_prompt_is_ignored(self, system_prompt):
        """Test that empty or whitespace-only system prompts are not sent."""
        request = InferenceRequest(
            model="m", message="Hello", system_prompt=system_prompt
        )

        assert BaseProvider._build_messages(request) == [
            {"role": "user", "content": "Hello"}
        ]

    def test_system_prompt_precedes_context(self):
        """Test ordering: system prompt, then context, then current message."""
        request = InferenceRequest(
            model="m",
            message="And now?",
            context=[
                ContextMessage(role=Role.USER, content="Hi"),
                ContextMessage(role=Role.ASSISTANT, content="Hello!"),
            ],
            system_prompt="Be concise.",
        )

        assert BaseProvider._build_messages(request) == [
            {"role": "system", "content": "Be concise."},
            {"role": "user", "content": "Hi"},
            {"role": "assistant", "content": "Hello!"},
            {"role": "user", "content": "And now?"},
        ]

    def test_roles_are_strings(self):
        """Test that roles are plain strings rather than Role enum members."""
        request = InferenceRequest(
            model="m",
            message="Hello",
            context=[ContextMessage(role=Role.ASSISTANT, content="Hi")],
            system_prompt="Be concise.",
        )

        roles = [m["role"] for m in BaseProvider._build_messages(request)]

        assert all(type(role) is str for role in roles)


class TestContextMessageRoles:
    """Tests that the system role is only settable through system_prompt."""

    def test_system_role_rejected_in_context(self):
        """Test that ContextMessage does not accept the system role."""
        with pytest.raises(ValueError):
            ContextMessage(role=Role.SYSTEM, content="Be concise.")
