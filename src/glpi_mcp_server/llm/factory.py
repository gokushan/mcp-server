from ..config import settings
from .strategies import LLMStrategy, OpenAIStrategy, AnthropicStrategy, OllamaStrategy

_STRATEGIES: dict[str, type[LLMStrategy]] = {
    "openai": OpenAIStrategy,
    "anthropic": AnthropicStrategy,
    "ollama": OllamaStrategy
}

def get_llm_strategy() -> LLMStrategy:
    """Get the appropriate LLM strategy based on configuration."""
    if settings.llm_mock:
        from .strategies import MockStrategy
        return MockStrategy()
        
    provider = settings.llm_provider
    strategy_class = _STRATEGIES.get(provider)
    
    if not strategy_class:
        raise ValueError(f"Unsupported LLM Provider: {provider}")
        
    return strategy_class()
