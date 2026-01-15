# azure-openai-provider Specification

## Purpose

Provide a fully functional Azure OpenAI inference provider that enables cloud-based AI model inference through the unified client interface, supporting chat completions with robust error handling and configuration validation.

## Requirements

### Requirement: Azure OpenAI Provider Registration
The system SHALL register Azure OpenAI as an available inference provider that can be instantiated through the unified client interface.

#### Scenario: Provider initialization with API key and endpoint
- **WHEN** AzureOpenAIProvider is instantiated with an API key and endpoint
- **THEN** it SHALL store the credentials securely
- **AND** it SHALL initialize the Azure OpenAI client

#### Scenario: Provider initialization with environment variables
- **WHEN** AzureOpenAIProvider is instantiated without explicit credentials
- **AND** AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT environment variables are set
- **THEN** it SHALL use the environment variable values
- **AND** it SHALL initialize successfully

#### Scenario: Provider initialization with custom configuration
- **WHEN** AzureOpenAIProvider is instantiated with custom api_version and timeout
- **THEN** it SHALL use the specified configuration
- **AND** it SHALL validate all required parameters are present

### Requirement: Chat Interface
The Azure OpenAI provider SHALL support chat-based interactions with conversation history.

#### Scenario: Single message chat
- **WHEN** predict() is called with a single message
- **THEN** it SHALL format the message for Azure OpenAI's chat completions API
- **AND** it SHALL return the assistant's response

#### Scenario: Multi-turn conversation
- **WHEN** predict() is called with a conversation history (context)
- **THEN** it SHALL maintain the conversation context
- **AND** it SHALL return contextually appropriate responses

#### Scenario: Deployment specification
- **WHEN** predict() is called with a model/deployment name
- **THEN** it SHALL use that deployment for the request
- **AND** the deployment name corresponds to an Azure OpenAI deployment, not a model name

### Requirement: Deployment Management
The Azure OpenAI provider SHALL acknowledge Azure's deployment-based architecture.

#### Scenario: Deployment listing
- **WHEN** supported_models() is called
- **THEN** it SHALL return an empty list
- **AND** this reflects Azure's API limitation (deployments not queryable via API)

#### Scenario: Factory method with deployments parameter
- **WHEN** InferenceClient.create_azure_openai_client() is called with a deployments list
- **THEN** it SHALL set the provider's models to the provided deployment names
- **AND** model validation in InferenceClient.predict() SHALL succeed for listed deployments

#### Scenario: Factory method without deployments parameter
- **WHEN** InferenceClient.create_azure_openai_client() is called without deployments
- **THEN** model validation SHALL fail for any model name
- **AND** InferenceClient.predict() SHALL raise InferenceRequestError

#### Scenario: Deployment not found
- **WHEN** a non-existent deployment name is used
- **THEN** it SHALL raise InferenceRequestError
- **AND** the error message SHALL indicate the deployment was not found

### Requirement: Error Handling
The Azure OpenAI provider SHALL handle various error conditions gracefully with informative messages.

#### Scenario: Invalid API key
- **WHEN** an invalid or missing API key is provided
- **THEN** it SHALL raise a ConfigurationError with clear guidance
- **AND** the error message SHALL indicate the API key is invalid

#### Scenario: Missing endpoint
- **WHEN** no endpoint is provided and AZURE_OPENAI_ENDPOINT is not set
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
- **WHEN** the connection to Azure OpenAI fails
- **THEN** it SHALL raise an InferenceRequestError
- **AND** the error SHALL indicate a connection problem

### Requirement: Configuration Validation
The Azure OpenAI provider SHALL validate all configuration parameters.

#### Scenario: Empty API key
- **WHEN** an empty string API key is provided
- **THEN** it SHALL raise ConfigurationError
- **AND** validation SHALL occur during initialization

#### Scenario: Invalid timeout
- **WHEN** a non-positive timeout value is provided
- **THEN** it SHALL raise ConfigurationError
- **AND** the error SHALL indicate timeout must be positive

## Implementation Notes

- Azure OpenAI uses "deployments" instead of model names. Users create deployments in Azure portal and reference them by deployment name.
- The `model` parameter in `InferenceRequest` should contain the deployment name, not the underlying model name (e.g., "my-gpt4-deployment" not "gpt-4").
- Azure OpenAI API does not provide an endpoint to list available deployments, so `supported_models()` returns an empty list.
- To enable model validation in `InferenceClient.predict()`, users must pass their deployment names via the `deployments` parameter when calling `InferenceClient.create_azure_openai_client()`.
- The `BaseProvider.models` setter was added to support providers that cannot dynamically discover available models.
