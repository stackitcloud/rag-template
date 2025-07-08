# Enhanced LLM Configuration System

This document explains the new enhanced LLM configuration system that provides a generic, configurable way to manage different LLM providers with Langfuse integration.

## Overview

The enhanced LLM configuration system consists of several key components:

1. **Provider Settings Classes**: Pydantic BaseSettings classes for each provider
2. **LLM Config Manager**: Central manager for provider configurations
3. **Factory Functions**: Helper functions to create configurations from various sources
4. **Langfuse Integration**: Enhanced integration with configurable fields

## Key Benefits

- ✅ **Generic Provider Support**: Add new providers easily with consistent interface
- ✅ **Langfuse Configuration**: Automatically expose configurable fields to Langfuse
- ✅ **Values.yaml Integration**: Configure everything through Kubernetes values
- ✅ **Environment Variables**: Fallback to environment-based configuration
- ✅ **Backward Compatibility**: Existing configurations continue to work
- ✅ **Type Safety**: Full Pydantic validation and type hints

## Supported Providers

| Provider | Description | LangChain Provider | Status |
|----------|-------------|-------------------|---------|
| `stackit` | STACKIT vLLM service | `openai` | ✅ Implemented |
| `gemini` | Google Gemini models | `google-genai` | ✅ Implemented |
| `ollama` | Local Ollama models | `ollama` | ✅ Implemented |

## Configuration Structure

### 1. Provider Settings Classes

Each provider has a dedicated settings class that inherits from `BaseLLMProviderSettings`:

```python
class StackitProviderSettings(BaseLLMProviderSettings):
    provider_name: str = "openai"  # Uses OpenAI-compatible API
    model: str = Field(default="cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic")
    base_url: str = Field(default="https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1")
    temperature: float = Field(default=0.0, title="LLM Temperature")
    top_p: float = Field(default=0.1, title="LLM Top P")
    # ... other provider-specific fields
```

### 2. Values.yaml Configuration

Configure providers in your `values.yaml`:

```yaml
backend:
  secrets:
    llmProviders:
      stackit:
        apiKey: "sk-your-stackit-api-key"
      gemini:
        apiKey: "your-google-api-key"

  envs:
    llmProviders:
      stackit:
        model: "cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic"
        base_url: "https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1"
        temperature: 0.0
        top_p: 0.1

      gemini:
        model: "gemini-1.5-pro"
        temperature: 0.7
        max_output_tokens: 8192
        top_p: 0.95
        top_k: 40

      ollama:
        model: "llama3:instruct"
        base_url: "http://localhost:11434"
        temperature: 0.0

    ragClassTypes:
      RAG_CLASS_TYPE_LLM_TYPE: "stackit"  # Select active provider
```

### 3. Environment Variables

Fallback to environment variables when values.yaml is not available:

```bash
# STACKIT
export STACKIT_VLLM_API_KEY="sk-your-api-key"
export STACKIT_VLLM_MODEL="cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic"
export STACKIT_VLLM_BASE_URL="https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1"

# Gemini
export GEMINI_API_KEY="your-google-api-key"
export GEMINI_MODEL="gemini-1.5-pro"
export GEMINI_TEMPERATURE="0.7"

# Ollama
export OLLAMA_MODEL="llama3:instruct"
export OLLAMA_BASE_URL="http://localhost:11434"
export OLLAMA_TEMPERATURE="0.0"

# Provider Selection
export RAG_CLASS_TYPE_LLM_TYPE="stackit"
```

## Usage Examples

### 1. Basic Usage in Dependency Container

```python
from rag_core_lib.impl.llm_config.llm_config_manager import LLMConfigManager
from rag_core_lib.impl.llms.llm_factory import create_chat_model_from_config

# Create configuration manager
llm_config_manager = LLMConfigManager(config_map)

# Create chat model for specific provider
chat_model = create_chat_model_from_config(
    config_manager=llm_config_manager,
    provider_name="stackit"
)
```

### 2. Enhanced Langfuse Integration

```python
# LangfuseManager now supports enhanced configuration
langfuse_manager = LangfuseManager(
    langfuse=langfuse,
    managed_prompts=prompts,
    llm=chat_model,
    llm_config_manager=llm_config_manager,  # Enhanced feature
    provider_name="stackit"                   # Enhanced feature
)
```

### 3. Factory-based Configuration

```python
from rag_core_lib.impl.llm_config.llm_config_factory import LLMConfigFactory

# From values.yaml
config_manager = LLMConfigFactory.from_values_yaml("/path/to/values.yaml")

# From environment variables
config_manager = LLMConfigFactory.from_environment()
```

## Adding New Providers

### Provider Support Table

| Provider | Class | LangChain Provider | Configurable Fields |
|----------|-------|-------------------|-------------------|
| STACKIT | `StackitProviderSettings` | `openai` | temperature, top_p, max_tokens, frequency_penalty, presence_penalty |
| Gemini | `GeminiProviderSettings` | `google-genai` | temperature, max_output_tokens, top_p, top_k |
| Ollama | `OllamaProviderSettings` | `ollama` | temperature, top_k, top_p |

To add a new provider (e.g., Azure OpenAI):

### 1. Create Provider Settings Class

```python
class AzureOpenAIProviderSettings(BaseLLMProviderSettings):
    class Config:
        env_prefix = "AZURE_OPENAI_"
        case_sensitive = False

    provider_name: str = Field(default="azure-openai", exclude=True)
    model: str = Field(default="gpt-4")
    api_key: str
    azure_endpoint: str
    api_version: str = Field(default="2024-02-01")
    temperature: float = Field(default=0.7, title="LLM Temperature")
    max_tokens: Optional[int] = Field(default=None, title="LLM Max Tokens")

    def get_provider_kwargs(self) -> Dict[str, Any]:
        return self.model_dump(exclude={"provider_name"})

    def get_configurable_fields(self) -> Dict[str, str]:
        return {
            "temperature": "LLM Temperature",
            "max_tokens": "LLM Max Tokens",
        }
```

### 2. Register in LLMConfigManager

```python
PROVIDER_SETTINGS: Dict[str, Type[BaseLLMProviderSettings]] = {
    "stackit": StackitProviderSettings,
    "gemini": GeminiProviderSettings,
    "ollama": OllamaProviderSettings,
    "azure-openai": AzureOpenAIProviderSettings,  # Add new provider
}
```

### 3. Update Provider Mapping

```python
def get_langchain_provider_name(self, provider_name: str) -> str:
    provider_mapping = {
        "stackit": "openai",  # STACKIT uses OpenAI-compatible API
        "azure-openai": "azure-openai",  # Map to LangChain provider name
        # ... existing mappings
    }
    return provider_mapping.get(provider_name, provider_name)
```

## Langfuse Configuration

### Configurable Fields

Fields with `title` in their Field definition are automatically exposed to Langfuse:

```python
temperature: float = Field(default=0.7, title="LLM Temperature")  # ✅ Configurable
api_key: str                                                      # ❌ Not configurable
```

### Langfuse UI Integration

The enhanced system automatically:

1. Creates Langfuse prompts with configurable parameters
2. Exposes provider-specific fields for runtime adjustment
3. Filters out sensitive fields (API keys) from configuration
4. Provides meaningful display names for parameters

## Migration Guide

### From Legacy Configuration

The new system is backward compatible. Existing configurations continue to work:

```python
# Legacy (still works)
large_language_model = Selector(
    class_selector_config.llm_type,
    ollama=Singleton(chat_model_provider, ollama_settings, "ollama"),
    stackit=Singleton(chat_model_provider, stackit_vllm_settings, "openai"),
)

# Enhanced (new)
enhanced_large_language_model = Selector(
    class_selector_config.llm_type,
    ollama=Singleton(create_chat_model_from_config, llm_config_manager, "ollama"),
    stackit=Singleton(create_chat_model_from_config, llm_config_manager, "stackit"),
)
```

### Recommended Migration Steps

1. **Phase 1**: Deploy enhanced system alongside legacy (both work)
2. **Phase 2**: Update values.yaml to use new configuration structure
3. **Phase 3**: Switch dependency injection to use enhanced providers
4. **Phase 4**: Remove legacy configurations (optional)

## Troubleshooting

### Common Issues

1. **Provider not found**: Check provider name matches registered providers
2. **Missing API key**: Verify API key is set in secrets or environment variables
3. **Langfuse configuration not working**: Ensure fields have `title` attribute
4. **Model not loading**: Check model name and provider availability

### Debug Configuration

```python
# List available providers
config_manager = LLMConfigManager(config_map)
providers = config_manager.list_available_providers()
print(f"Available providers: {providers}")

# Check configurable fields
fields = config_manager.get_configurable_fields("stackit")
print(f"Configurable fields: {fields}")

# Validate provider settings
settings = config_manager.get_provider_settings("stackit")
print(f"Provider settings: {settings}")
```

## Best Practices

1. **Use values.yaml**: Prefer values.yaml over environment variables for production
2. **Secure API keys**: Store API keys in Kubernetes secrets, not in values files
3. **Provider selection**: Use environment variables for provider selection to enable easy switching
4. **Validation**: Leverage Pydantic validation for configuration correctness
5. **Monitoring**: Use Langfuse to monitor and adjust LLM parameters in real-time

## Future Enhancements

Planned improvements:

- [ ] **Auto-discovery**: Automatic provider detection from installed packages
- [ ] **Configuration validation**: Real-time validation of provider configurations
- [ ] **Performance monitoring**: Built-in metrics for different providers
- [ ] **Cost tracking**: Integration with provider billing APIs
- [ ] **A/B testing**: Support for provider comparison and testing
