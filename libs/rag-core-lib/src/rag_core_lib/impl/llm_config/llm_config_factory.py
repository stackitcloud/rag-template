"""Factory for creating LLM configurations from values.yaml."""

import os
from typing import Dict, Any, Optional
import yaml
from rag_core_lib.impl.llm_config.llm_config_manager import LLMConfigManager


class LLMConfigFactory:
    """Factory for creating LLM configurations from various sources."""

    @staticmethod
    def from_values_yaml(values_yaml_path: Optional[str] = None) -> LLMConfigManager:
        """
        Create LLMConfigManager from values.yaml file.

        Parameters
        ----------
        values_yaml_path : Optional[str]
            Path to values.yaml file. If None, will look for environment variable
            VALUES_YAML_PATH or default to './values.yaml'

        Returns
        -------
        LLMConfigManager
            Configured manager instance
        """
        if values_yaml_path is None:
            values_yaml_path = os.getenv('VALUES_YAML_PATH', './values.yaml')

        try:
            with open(values_yaml_path, 'r') as file:
                values_config = yaml.safe_load(file)
            return LLMConfigManager.from_values_yaml(values_config)
        except FileNotFoundError:
            # Fallback to environment-based configuration
            return LLMConfigFactory.from_environment()

    @staticmethod
    def from_environment() -> LLMConfigManager:
        """
        Create LLMConfigManager from environment variables.

        Returns
        -------
        LLMConfigManager
            Configured manager instance based on environment variables
        """
        config_map = {}

        # Gemini configuration
        if os.getenv('GEMINI_API_KEY'):
            config_map['gemini'] = {
                'model': os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'),
                'api_key': os.getenv('GEMINI_API_KEY'),
                'temperature': float(os.getenv('GEMINI_TEMPERATURE', '0.7')),
                'max_output_tokens': int(os.getenv('GEMINI_MAX_OUTPUT_TOKENS', '8192')) if os.getenv('GEMINI_MAX_OUTPUT_TOKENS') else None,
                'top_p': float(os.getenv('GEMINI_TOP_P', '0.95')),
                'top_k': int(os.getenv('GEMINI_TOP_K', '40')),
            }

        # STACKIT configuration
        if os.getenv('STACKIT_VLLM_API_KEY'):
            config_map['stackit'] = {
                'model': os.getenv('STACKIT_VLLM_MODEL', 'cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic'),
                'api_key': os.getenv('STACKIT_VLLM_API_KEY'),
                'base_url': os.getenv('STACKIT_VLLM_BASE_URL',
                                    'https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1'),
                'temperature': float(os.getenv('STACKIT_VLLM_TEMPERATURE', '0.0')),
                'top_p': float(os.getenv('STACKIT_VLLM_TOP_P', '0.1')),
            }

        # Ollama configuration
        config_map['ollama'] = {
            'model': os.getenv('OLLAMA_MODEL', 'llama3:instruct'),
            'base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'temperature': float(os.getenv('OLLAMA_TEMPERATURE', '0.0')),
            'top_k': int(os.getenv('OLLAMA_TOP_K', '0')),
            'top_p': float(os.getenv('OLLAMA_TOP_P', '0.0')),
        }

        return LLMConfigManager(config_map)

    @staticmethod
    def create_default_config(provider: str) -> Dict[str, Any]:
        """
        Create default configuration for a provider.

        Parameters
        ----------
        provider : str
            The provider name

        Returns
        -------
        Dict[str, Any]
            Default configuration for the provider
        """
        defaults = {
            'stackit': {
                'model': 'cortecs/Llama-3.3-70B-Instruct-FP8-Dynamic',
                'base_url': 'https://api.openai-compat.model-serving.eu01.onstackit.cloud/v1',
                'temperature': 0.0,
                'top_p': 0.1,
            },
            'gemini': {
                'model': 'gemini-1.5-pro',
                'temperature': 0.7,
                'max_output_tokens': 8192,
                'top_p': 0.95,
                'top_k': 40,
            },
            'ollama': {
                'model': 'llama3:instruct',
                'base_url': 'http://localhost:11434',
                'temperature': 0.0,
                'top_k': 0,
                'top_p': 0.0,
            }
        }

        return defaults.get(provider, {})
