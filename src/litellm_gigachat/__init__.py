"""
LiteLLM GigaChat Integration

Полнофункциональная интеграция GigaChat API с LiteLLM.
"""

from .core import TokenManager, get_global_token_manager, get_gigachat_token
from .callbacks import (
    GigaChatTokenCallback, 
    get_gigachat_callback, 
    setup_litellm_gigachat_integration,
    GigaChatTransformer,
    get_gigachat_transformer,
    setup_gigachat_transformer,
    get_gigachat_transformer_stats
)
from .proxy import start_proxy_server, main

__version__ = "0.1.1"
__author__ = "LiteLLM GigaChat Team"

__all__ = [
    # Core
    'TokenManager',
    'get_global_token_manager', 
    'get_gigachat_token',
    # Callbacks
    'GigaChatTokenCallback',
    'get_gigachat_callback',
    'setup_litellm_gigachat_integration',
    'GigaChatTransformer',
    'get_gigachat_transformer',
    'setup_gigachat_transformer',
    'get_gigachat_transformer_stats',
    # Proxy
    'start_proxy_server',
    'main'
]
