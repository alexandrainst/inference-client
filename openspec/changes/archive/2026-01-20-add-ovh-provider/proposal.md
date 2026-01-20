# Add OVH Provider

**Change ID**: `add-ovh-provider`  
**Status**: Draft  
**Created**: 2026-01-16  
**Author**: System

## Summary

Add support for OVH AI as an inference provider to enable cloud-based AI model inference through the unified client interface. This allows users to leverage OVH's French cloud infrastructure for AI workloads with OpenAI-compatible API.

## Motivation

- **European Sovereignty**: Utilize French cloud infrastructure for data residency compliance
- **OpenAI Compatibility**: Seamless integration with existing OpenAI-based workflows
- **Cost Efficiency**: Competitive pricing for AI inference in European market
- **Reliability**: OVH's robust cloud infrastructure and SLAs
- **Model Variety**: Access to various AI models through OVH's platform
- **Compliance**: GDPR-compliant AI services within EU borders

## Scope

This change adds a new inference provider without modifying existing provider interfaces or the core client API. It's an additive feature that extends the current provider ecosystem.

### In Scope
- Complete OVHProvider class implementation
- OVH AI API integration (OpenAI-compatible)
- Chat-based interactions
- Comprehensive error handling
- Unit and integration tests

### Out of Scope
- Text generation and completion beyond chat
- Streaming response support
- OVH account setup automation
- Custom model training capabilities
- Multi-region load balancing
- Advanced billing analytics

## Dependencies

- **Runtime**: `openai` Python package (already in requirements.txt for compatibility)
- **Development**: OVH AI API access for testing
- **System**: Compatible with existing httpx/pydantic infrastructure

## Breaking Changes

None. This is a pure addition that maintains backward compatibility.

## Success Criteria

- [ ] OVHProvider can be instantiated and configured
- [ ] Chat completions work with OVH AI models
- [ ] Error handling covers common failure scenarios
- [ ] Unit tests achieve 80%+ coverage
- [ ] Integration tests pass with OVH AI service
- [ ] Documentation includes setup and usage examples