"""
OVH AI inference provider implementation.

This provider uses OVH's hosted AI service, which is OpenAI-compatible.
OVH AI provides European-hosted inference with GDPR compliance.

This requires:
- An OVH API key
- An OVH AI endpoint URL
- A model name from available OVH AI models

It is a thin specialisation of :class:`OpenAICompatibleProvider`: OVH speaks
the standard OpenAI chat-completions protocol, so all behaviour is inherited
and only the naming and environment-variable fallbacks are customised.
"""

from inference_client.providers.openai_compatible import OpenAICompatibleProvider


class OVHProvider(OpenAICompatibleProvider):
    """
    OVH AI inference provider.

    OVH AI is OpenAI-compatible, so it uses standard model names and the same
    request/response handling as any other OpenAI-compatible endpoint. When
    ``api_key`` / ``base_url`` are not passed explicitly, they fall back to the
    ``OVH_API_KEY`` / ``OVH_AI_ENDPOINT`` environment variables.
    """

    provider_name = "OVH AI"
    api_key_env = "OVH_API_KEY"
    base_url_env = "OVH_AI_ENDPOINT"
    require_https = True
