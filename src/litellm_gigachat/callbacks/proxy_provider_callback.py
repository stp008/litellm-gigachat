import logging
from typing import Optional, Dict, Any, Literal
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from ..core.proxy_provider_manager import get_global_multi_proxy_provider_manager

logger = logging.getLogger(__name__)

class ProxyProviderCallback(CustomLogger):
    """
    Callback для LiteLLM Proxy, который автоматически добавляет заголовки 
    для прокси-провайдеров (кастомные API endpoints)
    """
    
    def __init__(self):
        super().__init__()
        self.multi_manager = get_global_multi_proxy_provider_manager()
        
    async def async_pre_call_hook(
        self, 
        user_api_key_dict: UserAPIKeyAuth, 
        cache: DualCache, 
        data: dict, 
        call_type: Literal[
            "completion",
            "text_completion", 
            "embeddings",
            "image_generation",
            "moderation",
            "audio_transcription",
        ]
    ) -> dict:
        """
        Вызывается перед каждым API запросом в LiteLLM Proxy.
        Автоматически добавляет заголовки для моделей прокси-провайдеров.
        """
        logger.debug("ProxyProvider async_pre_call_hook вызван")
        
        try:
            # Получаем модель из данных запроса
            model = data.get('model', '')
            logger.debug(f"Обрабатываем модель: {model}")
            
            # Находим провайдера для этой модели
            provider = self.multi_manager.get_provider_by_suffix(model)
            
            if provider:
                logger.info(f"Добавляем заголовки для модели {model} (провайдер: {provider.name})")
                
                # Получаем заголовки аутентификации для этого провайдера
                auth_headers = provider.get_auth_headers()
                logger.debug(f"Заголовки аутентификации: {list(auth_headers.keys())}")
                
                # Получаем URL провайдера
                provider_url = provider.url
                
                if provider_url:
                    # Обновляем URL на прокси-провайдер
                    if 'litellm_params' in data:
                        data['litellm_params']['api_base'] = provider_url
                        logger.debug(f"URL обновлен в litellm_params: {provider_url}")
                    else:
                        data['api_base'] = provider_url
                        logger.debug(f"URL обновлен в data: {provider_url}")
                
                # Добавляем заголовки аутентификации
                if auth_headers:
                    # В LiteLLM Proxy заголовки могут передаваться через extra_headers
                    if 'litellm_params' in data:
                        if 'extra_headers' not in data['litellm_params']:
                            data['litellm_params']['extra_headers'] = {}
                        data['litellm_params']['extra_headers'].update(auth_headers)
                        logger.debug("Заголовки добавлены в litellm_params.extra_headers")
                    else:
                        if 'extra_headers' not in data:
                            data['extra_headers'] = {}
                        data['extra_headers'].update(auth_headers)
                        logger.debug("Заголовки добавлены в data.extra_headers")
                    
                    # Также добавляем в headers если есть
                    if 'headers' in data:
                        data['headers'].update(auth_headers)
                        logger.debug("Заголовки добавлены в data.headers")
                
                # Убираем api_key для моделей прокси-провайдера (не используется)
                if 'litellm_params' in data:
                    data['litellm_params']['api_key'] = "none"
                    logger.debug("api_key установлен в 'none' для модели прокси-провайдера")
                else:
                    data['api_key'] = "none"
                    logger.debug("api_key установлен в 'none' для модели прокси-провайдера")
                
                logger.info(f"Заголовки и URL успешно настроены для модели {model} (провайдер: {provider.name})")
            else:
                logger.debug(f"Модель {model} не является моделью прокси-провайдера")
                
        except Exception as e:
            logger.error(f"Ошибка при настройке заголовков для модели прокси-провайдера: {e}")
            # Не прерываем выполнение, позволяем LiteLLM попробовать с текущими настройками
        
        return data
    
    async def async_post_call_failure_hook(
        self,
        request_data: dict,
        original_exception: Exception,
        user_api_key_dict: UserAPIKeyAuth,
        traceback_str: Optional[str] = None,
    ):
        """
        Вызывается при ошибке API запроса в LiteLLM Proxy.
        Обрабатываем ошибки для моделей прокси-провайдеров.
        """
        try:
            # Получаем модель из данных запроса
            model = request_data.get('model', '')
            
            # Находим провайдера для этой модели
            provider = self.multi_manager.get_provider_by_suffix(model)
            
            if provider:
                # Проверяем различные типы ошибок
                error_message = str(original_exception).lower()
                
                if ('401' in error_message or 
                    'unauthorized' in error_message or 
                    'authentication' in error_message or
                    'forbidden' in error_message or
                    'invalid' in error_message):
                    
                    logger.warning(f"Ошибка аутентификации для модели {model} (провайдер: {provider.name})")
                    logger.debug(f"Ошибка: {original_exception}")
                    
                    # Логируем информацию о конфигурации для отладки
                    config_info = self.multi_manager.get_configuration_info()
                    logger.debug(f"Конфигурация прокси-провайдеров: {config_info}")
                
        except Exception as e:
            logger.error(f"Ошибка в async_post_call_failure_hook для модели прокси-провайдера: {e}")
    
    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        """
        Вызывается после успешного API запроса.
        Логируем успешные запросы к моделям прокси-провайдеров.
        """
        try:
            model = data.get('model', '')
            provider = self.multi_manager.get_provider_by_suffix(model)
            if provider:
                logger.debug(f"Успешный запрос к модели {model} (провайдер: {provider.name})")
        except Exception as e:
            logger.error(f"Ошибка в async_post_call_success_hook для модели прокси-провайдера: {e}")


# Глобальный экземпляр callback
_proxy_provider_callback: Optional[ProxyProviderCallback] = None

def get_proxy_provider_callback() -> ProxyProviderCallback:
    """Получение глобального экземпляра ProxyProviderCallback"""
    global _proxy_provider_callback
    if _proxy_provider_callback is None:
        _proxy_provider_callback = ProxyProviderCallback()
    return _proxy_provider_callback

# Создаем экземпляр для использования в конфигурации
proxy_provider_callback_instance = get_proxy_provider_callback()

def setup_litellm_proxy_provider_integration():
    """
    Настройка интеграции прокси-провайдера с LiteLLM
    """
    import litellm
    
    # Добавляем callback в LiteLLM
    callback = get_proxy_provider_callback()
    
    # Проверяем, не добавлен ли уже callback
    if callback not in litellm.callbacks:
        litellm.callbacks.append(callback)
        logger.info("ProxyProvider callback добавлен в LiteLLM")
    else:
        logger.debug("ProxyProvider callback уже добавлен в LiteLLM")
