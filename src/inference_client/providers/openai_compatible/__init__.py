"""
Generic OpenAI-compatible inference provider.

This module provides support for any inference server that exposes the
OpenAI chat-completions API (``/v1/chat/completions`` and ``/v1/models``),
such as vLLM, Text Generation Inference, OpenRouter, OVH AI and others.
Provider-specific implementations (e.g. OVH) build on top of it.
"""

from .openai_compatible_provider import OpenAICompatibleProvider

__all__ = ["OpenAICompatibleProvider"]
