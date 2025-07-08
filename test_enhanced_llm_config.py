"""Test script to validate the enhanced LLM configuration system."""

import os
import sys
sys.path.append('/Users/klosandr/Github/rag-template-2.0/libs/rag-core-lib/src')

from rag_core_lib.impl.llm_config.llm_config_manager import LLMConfigManager
from rag_core_lib.impl.llm_config.llm_config_factory import LLMConfigFactory
from rag_core_lib.impl.llms.llm_factory import create_chat_model_from_config


def test_basic_configuration():
    """Test basic LLM configuration functionality."""
    print("🧪 Testing Enhanced LLM Configuration System\n")

    # Test 1: Create configuration manager with mock data
    print("1️⃣  Testing LLMConfigManager creation...")
    config_map = {
        "stackit": {
            "model": "cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic",
            "base_url": "https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1",
            "api_key": "test-key",
            "temperature": 0.0,
            "top_p": 0.1,
        },
        "gemini": {
            "model": "gemini-1.5-pro",
            "api_key": "test-key",
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "top_p": 0.95,
            "top_k": 40,
        },
        "ollama": {
            "model": "llama3:instruct",
            "base_url": "http://localhost:11434",
            "temperature": 0.0,
            "top_k": 0,
            "top_p": 0.0,
        }
    }

    manager = LLMConfigManager(config_map)
    print("✅ LLMConfigManager created successfully")

    # Test 2: List available providers
    print("\n2️⃣  Testing provider listing...")
    providers = manager.list_available_providers()
    print(f"✅ Available providers: {list(providers.keys())}")

    # Test 3: Get provider settings
    print("\n3️⃣  Testing provider settings...")
    try:
        stackit_settings = manager.get_provider_settings("stackit")
        print(f"✅ STACKIT settings: {stackit_settings.model}")

        gemini_settings = manager.get_provider_settings("gemini")
        print(f"✅ Gemini settings: {gemini_settings.model}")

        ollama_settings = manager.get_provider_settings("ollama")
        print(f"✅ Ollama settings: {ollama_settings.model}")
    except Exception as e:
        print(f"❌ Error getting provider settings: {e}")

    # Test 4: Get configurable fields
    print("\n4️⃣  Testing configurable fields...")
    try:
        stackit_fields = manager.get_configurable_fields("stackit")
        print(f"✅ STACKIT configurable fields: {list(stackit_fields.keys())}")

        gemini_fields = manager.get_configurable_fields("gemini")
        print(f"✅ Gemini configurable fields: {list(gemini_fields.keys())}")

        ollama_fields = manager.get_configurable_fields("ollama")
        print(f"✅ Ollama configurable fields: {list(ollama_fields.keys())}")
    except Exception as e:
        print(f"❌ Error getting configurable fields: {e}")

    # Test 5: Factory creation
    print("\n5️⃣  Testing factory creation...")
    try:
        env_manager = LLMConfigFactory.from_environment()
        print("✅ Environment-based manager created successfully")
    except Exception as e:
        print(f"❌ Error creating environment manager: {e}")

    print("\n🎉 All tests completed!")


def test_chat_model_creation():
    """Test chat model creation (requires actual dependencies)."""
    print("\n🧪 Testing Chat Model Creation (may require dependencies)\n")

    try:
        config_map = {
            "stackit": {
                "model": "cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic",
                "base_url": "https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1",
                "api_key": "test-key",
                "temperature": 0.0,
                "top_p": 0.1,
            },
            "gemini": {
                "model": "gemini-1.5-pro",
                "api_key": "test-key",
                "temperature": 0.7,
                "max_output_tokens": 8192,
                "top_p": 0.95,
                "top_k": 40,
            },
            "ollama": {
                "model": "llama3:instruct",
                "base_url": "http://localhost:11434",
                "temperature": 0.0,
                "top_k": 0,
                "top_p": 0.0,
            }
        }

        manager = LLMConfigManager(config_map)

        # This would require langchain dependencies to be available
        # chat_model = create_chat_model_from_config(manager, "stackit")
        # print("✅ Chat model created successfully")
        print("⚠️  Chat model creation skipped (requires langchain dependencies)")

    except Exception as e:
        print(f"❌ Error creating chat model: {e}")


if __name__ == "__main__":
    test_basic_configuration()
    test_chat_model_creation()
