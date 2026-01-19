# ovh-provider Specification

## Purpose

Provide a fully functional OVH AI inference provider that enables cloud-based AI model inference through the unified client interface, supporting chat completions with robust error handling and configuration validation using OVH's OpenAI-compatible API.

## ADDED Requirements

### Requirement: OVH AI Provider Registration
The system SHALL register OVH AI as an available inference provider that can be instantiated through the unified client interface.

#### Scenario: Provider initialization with API key and endpoint
- **WHEN** OVHProvider is instantiated with an API key and endpoint
- **THEN** it SHALL store the credentials securely
- **AND** it SHALL initialize the OVH AI client

#### Scenario: Provider initialization with environment variables
- **WHEN** OVHProvider is instantiated without explicit credentials
- **AND** OVH_API_KEY and OVH_AI_ENDPOINT environment variables are set
- **THEN** it SHALL use the environment variable values
- **AND** it SHALL initialize successfully

#### Scenario: Provider initialization with custom configuration
- **WHEN** OVHProvider is instantiated with custom api_version and timeout
- **THEN** it SHALL use the specified configuration
- **AND** it SHALL validate all required parameters are present

### Requirement: OVH AI Chat Interface
The OVH provider SHALL support chat-based interactions with conversation history.

#### Scenario: Single message chat
- **WHEN** predict() is called with a single message
- **THEN** it SHALL format the message for OVH AI's chat completions API
- **AND** it SHALL return the assistant's response

#### Scenario: Multi-turn conversation
- **WHEN** predict() is called with a conversation history (context)
- **THEN** it SHALL maintain the conversation context
- **AND** it SHALL return contextually appropriate responses

#### Scenario: Model specification
- **WHEN** predict() is called with a model name
- **THEN** it SHALL use that model for the request
- **AND** the model name corresponds to an available OVH AI model

### Requirement: OVH AI Model Management
The OVH provider SHALL provide utilities for interacting with available models.

#### Scenario: Model listing
- **WHEN** supported_models() is called
- **THEN** it SHALL return a list of available models from OVH AI
- **AND** it SHALL cache the list for performance

#### Scenario: Model availability check
- **WHEN** a specific model is requested
- **THEN** it SHALL verify the model is available in OVH AI
- **AND** it SHALL provide clear feedback if model is not supported

#### Scenario: Model not found
- **WHEN** a non-existent model name is used
- **THEN** it SHALL raise InferenceRequestError
- **AND** the error message SHALL indicate the model was not found

### Requirement: OVH AI Error Handling
The OVH provider SHALL handle various error conditions gracefully with informative messages.

#### Scenario: Invalid API key
- **WHEN** an invalid or missing API key is provided
- **THEN** it SHALL raise a ConfigurationError with clear guidance
- **AND** the error message SHALL indicate the API key is invalid

#### Scenario: Missing endpoint
- **WHEN** no endpoint is provided and OVH_AI_ENDPOINT is not set
- **THEN** it SHALL raise a ConfigurationError
- **AND** the error message SHALL explain endpoint is required

#### Scenario: Invalid endpoint format
- **WHEN** an endpoint not starting with https:// is provided
- **THEN** it SHALL raise a ConfigurationError
- **AND** the error message SHALL indicate HTTPS is required

#### Scenario: Rate limit exceeded
- **WHEN** the API rate limit is exceeded
- **THEN** it SHALL raise an InferenceRequestError
- **AND** the error SHALL include information about the rate limit

#### Scenario: Request timeout
- **WHEN** a request exceeds the configured timeout
- **THEN** it SHALL raise an InferenceTimeoutError
- **AND** the error SHALL include the timeout duration

#### Scenario: Connection failure
- **WHEN** the connection to OVH AI fails
- **THEN** it SHALL raise an InferenceRequestError
- **AND** the error SHALL indicate a connection problem

### Requirement: OVH AI Configuration Validation
The OVH provider SHALL validate configuration parameters to ensure proper operation.

#### Scenario: Valid configuration validation
- **WHEN** provider is configured with valid parameters
- **THEN** it SHALL accept the configuration without error
- **AND** it SHALL store the configuration for subsequent requests

#### Scenario: Invalid API key format
- **WHEN** provider is configured with an invalid API key format
- **THEN** it SHALL raise a ConfigurationError immediately
- **AND** the error SHALL specify what makes the key invalid

#### Scenario: Invalid endpoint URL
- **WHEN** provider is configured with an invalid endpoint URL
- **THEN** it SHALL raise a ConfigurationError
- **AND** the error SHALL explain proper URL format