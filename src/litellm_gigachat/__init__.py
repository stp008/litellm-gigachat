"""
LiteLLM GigaChat Integration

Полнофункциональная интеграция GigaChat API с LiteLLM.
"""

from .core import TokenManager, get_global_token_manager, get_gigachat_token
from .core.internal_header_manager import (
    InternalHeaderManager,
    get_global_internal_header_manager,
    get_internal_auth_headers,
    is_internal_gigachat_enabled
)
from .callbacks import (
    GigaChatTokenCallback, 
    get_gigachat_callback, 
    setup_litellm_gigachat_integration,
    GigaChatTransformer,
    get_gigachat_transformer,
    setup_gigachat_transformer,
    get_gigachat_transformer_stats
)
from .callbacks.internal_header_callback import (
    InternalHeaderCallback,
    get_internal_header_callback,
    setup_litellm_internal_gigachat_integration
)
from .proxy import start_proxy_server, main
from .cli.main import cli, main as cli_main

__version__ = "0.1.3"
__author__ = "LiteLLM GigaChat Team"

__all__ = [
    # Core
    'TokenManager',
    'get_global_token_manager', 
    'get_gigachat_token',
    # Internal Header Manager
    'InternalHeaderManager',
    'get_global_internal_header_manager',
    'get_internal_auth_headers',
    'is_internal_gigachat_enabled',
    # Callbacks
    'GigaChatTokenCallback',
    'get_gigachat_callback',
    'setup_litellm_gigachat_integration',
    'GigaChatTransformer',
    'get_gigachat_transformer',
    'setup_gigachat_transformer',
    'get_gigachat_transformer_stats',
    # Internal Header Callback
    'InternalHeaderCallback',
    'get_internal_header_callback',
    'setup_litellm_internal_gigachat_integration',
    # Proxy
    'start_proxy_server',
    'main'
]
