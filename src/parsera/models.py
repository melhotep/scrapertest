#!/usr/bin/env python3
"""
Parsera models module - Handles LLM model creation and configuration
"""

from typing import Optional
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Try to import optional dependencies
try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Default model to use when no configuration is provided
DEFAULT_MODEL_PROVIDER = "openai"
DEFAULT_MODEL_NAME = "gpt-4o-mini"


class ModelNotAvailableError(Exception):
    """Exception raised when a requested model is not available."""
    pass


def create_model_from_config(
    provider: str = DEFAULT_MODEL_PROVIDER,
    model_name: str = DEFAULT_MODEL_NAME,
    api_key: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """
    Create and configure an LLM model based on the provided configuration.
    
    Args:
        provider: The LLM provider (openai, anthropic, ollama, local)
        model_name: Name of the model to use
        api_key: API key for the selected provider
        **kwargs: Additional configuration options
        
    Returns:
        Configured LLM model
        
    Raises:
        ModelNotAvailableError: If the requested model/provider is not available
    """
    provider = provider.lower()
    
    if provider == "openai":
        # Use API key from config or environment variable
        if api_key:
            return ChatOpenAI(model_name=model_name, openai_api_key=api_key, **kwargs)
        else:
            return ChatOpenAI(model_name=model_name, **kwargs)
            
    elif provider == "anthropic":
        if not api_key:
            raise ValueError("API key is required for Anthropic models")
        return ChatAnthropic(model_name=model_name, anthropic_api_key=api_key, **kwargs)
        
    elif provider == "ollama":
        if not OLLAMA_AVAILABLE:
            raise ModelNotAvailableError(
                "Ollama support is not available. Install langchain-ollama package."
            )
        # Default to localhost:11434 if no base URL is provided
        base_url = kwargs.get("base_url", "http://localhost:11434")
        return ChatOllama(model=model_name, base_url=base_url, **kwargs)
        
    elif provider == "local":
        # This would be implemented with a local model running within the actor
        # For now, raise an error as this requires additional setup
        raise ModelNotAvailableError(
            "Local model support is not yet implemented in this version."
        )
        
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


# Default model implementation for standalone use
def get_default_model() -> BaseChatModel:
    """Get the default LLM model for extraction."""
    return ChatOpenAI(model_name=DEFAULT_MODEL_NAME)
