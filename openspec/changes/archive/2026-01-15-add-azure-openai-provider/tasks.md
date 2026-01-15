# Implementation Tasks: Add Azure OpenAI Provider

## Phase 1: Core Implementation

- [x] Add `openai` package to `requirements.txt`
- [x] Create the `AzureOpenAIProvider` class in `src/inference_client/providers/azure_openai/azure_openai_provider.py`
- [x] Implement `predict()` method using Azure OpenAI chat completions API
- [x] Implement `supported_models()` (returns empty list - Azure doesn't expose deployment listing via API)
- [x] Add configuration validation (API key, endpoint URL)
- [x] Add environment variable support (`AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`)

## Phase 2: Error Handling & Robustness

- [x] Handle authentication errors (invalid API key)
- [x] Handle rate limiting with appropriate error messages
- [x] Handle deployment not found errors
- [x] Handle bad request errors
- [x] Handle timeout scenarios with InferenceTimeoutError
- [x] Handle connection errors
- [x] Add request/response validation

## Phase 3: Testing

- [x] Create unit tests with mocked Azure OpenAI responses (23 test cases)
- [x] Create integration tests (with real Azure API)
- [x] Test error scenarios and edge cases
- [x] Verify type hints are complete and validated

## Phase 4: Documentation & Polish

- [x] Write comprehensive docstrings
- [x] Create usage examples in README
- [x] Add `create_azure_openai_client()` factory method to InferenceClient
- [x] Update main README with Azure OpenAI provider info
- [x] Final integration testing and validation

## Quality Gates

- [x] All unit tests pass (23/23)
- [x] Integration tests pass (with Azure credentials)
- [x] Code coverage >= 80% (achieved 91%)
- [x] Type hints complete and validated
- [x] Documentation review complete
- [x] OpenSpec validation passes
