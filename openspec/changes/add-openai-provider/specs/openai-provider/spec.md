# openai-provider Specification

## Purpose

Provide a fully functional OpenAI inference provider that enables cloud-based AI model inference through the unified client interface, supporting chat completions with robust error handling and configuration validation.

## ADDED Requirements

### Requirement: OpenAI Provider Registration
The system SHALL register OpenAI as an available inference provider that can be instantiated through the unified client interface.

#### Scenario: Provider initialization with API key
- **WHEN** OpenAIProvider is instantiated with an API key
- **THEN** it SHALL store the API key securely
- **AND** it SHALL initialize the OpenAI client

#### Scenario: Provider initialization with custom configuration
- **WHEN** OpenAIProvider is instantiated with custom base_url and model
- **THEN** it SHALL use the specified configuration
- **AND** it SHALL validate the API key is present

### Requirement: Chat Interface
The OpenAI provider SHALL support chat-based interactions with conversation history.

#### Scenario: Single message chat
- **WHEN** predict() is called with a single message
- **THEN** it SHALL format the message for OpenAI's chat completions API
- **AND** it SHALL return the assistant's response

#### Scenario: Multi-turn conversation
- **WHEN** predict() is called with a conversation history
- **THEN** it SHALL maintain the conversation context
- **AND** it SHALL return contextually appropriate responses

#### Scenario: Model specification
- **WHEN** predict() is called with a specific model name
- **THEN** it SHALL use that model for the request
- **AND** it SHALL validate the model is available

### Requirement: Model Management
The OpenAI provider SHALL provide utilities for interacting with available models.

#### Scenario: Model listing
- **WHEN** supported_models() is called
- **THEN** it SHALL return a list of available OpenAI models
- **AND** the list SHALL include common models like gpt-4, gpt-4o, gpt-3.5-turbo

#### Scenario: Model availability check
- **WHEN** checking if a specific model is available
- **THEN** it SHALL verify the model exists in the account's available models
- **AND** it SHALL provide clear feedback if model is not accessible

### Requirement: Environment Variable Support
The OpenAI provider SHALL support API key configuration via environment variable.

#### Scenario: API key from environment variable
- **WHEN** OpenAIProvider is instantiated without an explicit API key
- **AND** the OPENAI_API_KEY environment variable is set
- **THEN** it SHALL use the environment variable value
- **AND** it SHALL initialize successfully

### Requirement: Error Handling
The OpenAI provider SHALL handle various error conditions gracefully with informative messages.

#### Scenario: Invalid API key
- **WHEN** an invalid or missing API key is provided
- **THEN** it SHALL raise a ConfigurationError with clear guidance
- **AND** the error message SHALL indicate the API key is invalid

#### Scenario: Rate limit exceeded
- **WHEN** the API rate limit is exceeded
- **THEN** it SHALL raise an InferenceRequestError
- **AND** the error SHALL include retry-after information if available

#### Scenario: Model not found
- **WHEN** a specified model is not available
- **THEN** it SHALL raise an InferenceRequestError
- **AND** the error SHALL suggest valid model alternatives

#### Scenario: Request timeout
- **WHEN** a generation request exceeds the configured timeout
- **THEN** it SHALL raise an InferenceTimeoutError
- **AND** it SHALL cancel the underlying request cleanly

#### Scenario: Service unavailable
- **WHEN** OpenAI service is unavailable or returns server errors
- **THEN** it SHALL raise an InferenceRequestError with clear guidance
- **AND** the error message SHALL suggest checking OpenAI status page

### Requirement: Configuration Validation
The OpenAI provider SHALL validate configuration parameters to ensure proper operation.

#### Scenario: Valid configuration validation
- **WHEN** provider is configured with valid API key and parameters
- **THEN** it SHALL accept the configuration without error
- **AND** it SHALL store the configuration for subsequent requests

#### Scenario: Missing API key validation
- **WHEN** provider is instantiated without an API key
- **THEN** it SHALL raise a ConfigurationError immediately
- **AND** the error SHALL specify that an API key is required

#### Scenario: Invalid base URL validation
- **WHEN** provider is configured with an invalid base URL
- **THEN** it SHALL raise a ConfigurationError immediately
- **AND** the error SHALL specify what makes the URL invalid
