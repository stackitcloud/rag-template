#!/usr/bin/env python3
"""
Simple test script to verify the chat_model_provider function works correctly
with the new init_chat_model approach.
"""

import os
import sys
from pathlib import Path

# Add the libs path to Python path
libs_path = Path(__file__).parent / "libs" / "rag-core-lib" / "src"
sys.path.insert(0, str(libs_path))

from rag_core_lib.impl.llms.llm_factory import chat_model_provider
from rag_core_lib.impl.settings.stackit_vllm_settings import StackitVllmSettings

def test_chat_model_provider():
    """Test that the chat_model_provider function creates a model correctly."""
    
    # Set up test environment variables
    os.environ["STACKIT_VLLM_API_KEY"] = "test_key"
    os.environ["STACKIT_VLLM_BASE_URL"] = "https://test.example.com/v1"
    os.environ["STACKIT_VLLM_MODEL"] = "test-model"
    
    # Create settings
    settings = StackitVllmSettings()
    
    print(f"Settings model: {settings.model}")
    print(f"Settings api_key: {settings.api_key}")
    print(f"Settings base_url: {settings.base_url}")
    print(f"Settings temperature: {settings.temperature}")
    print(f"Settings top_p: {settings.top_p}")
    
    try:
        # Create chat model using the new provider
        chat_model = chat_model_provider(settings, "openai")
        print(f"✅ Successfully created chat model: {type(chat_model).__name__}")
        print(f"Model type: {type(chat_model)}")
        
        # Check if it has the expected attributes
        if hasattr(chat_model, 'model_name'):
            print(f"Model name: {chat_model.model_name}")
        if hasattr(chat_model, 'openai_api_base'):
            print(f"API base: {chat_model.openai_api_base}")
        if hasattr(chat_model, 'temperature'):
            print(f"Temperature: {chat_model.temperature}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error creating chat model: {e}")
        return False

if __name__ == "__main__":
    success = test_chat_model_provider()
    sys.exit(0 if success else 1)
