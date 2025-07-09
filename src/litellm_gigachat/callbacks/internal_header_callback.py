import logging
from typing import Optional, Dict, Any, Literal
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from ..core.internal_header_manager import get_global_internal_header_manager

logger = logging.getLogger(__name__)

class InternalHeaderCallback(CustomLogger):
    """
    Callback для LiteLLM Proxy, который автоматически добавляет заголовки 
    для внутренней установки GigaChat
    """
    
    def __init__(self):
        super().__init__()
        self.header_manager = get_global_internal_header_manager()
        
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
        Автоматически добавляет заголовки для внутренних моделей GigaChat.
        """
        logger.debug("Internal GigaChat async_pre_call_hook вызван")
        
        try:
            # Получаем модель из данных запроса
            model = data.get('model', '')
            logger.debug(f"Обрабатываем модель: {model}")
            
            # Проверяем, что это запрос к внутренней модели GigaChat
            if self._is_internal_gigachat_model(model, data):
                logger.info(f"Добавляем заголовки для внутренней модели GigaChat: {model}")
                
                # Получаем заголовки аутентификации
                auth_headers = self.header_manager.get_auth_headers()
                logger.debug(f"Заголовки аутентификации: {list(auth_headers.keys())}")
                
                # Получаем URL внутренней установки
                internal_url = self.header_manager.get_internal_url()
                
                if internal_url:
                    # Обновляем URL на внутренний
                    if 'litellm_params' in data:
                        data['litellm_params']['api_base'] = internal_url
                        logger.debug(f"URL обновлен в litellm_params: {internal_url}")
                    else:
                        data['api_base'] = internal_url
                        logger.debug(f"URL обновлен в data: {internal_url}")
                
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
                
                # Убираем api_key для внутренних моделей (не используется)
                if 'litellm_params' in data:
                    data['litellm_params']['api_key'] = "none"
                    logger.debug("api_key установлен в 'none' для внутренней модели")
                else:
                    data['api_key'] = "none"
                    logger.debug("api_key установлен в 'none' для внутренней модели")
                
                logger.info(f"Заголовки и URL успешно настроены для внутренней модели {model}")
            else:
                logger.debug(f"Модель {model} не является внутренней моделью GigaChat")
                
        except Exception as e:
            logger.error(f"Ошибка при настройке заголовков для внутренней модели: {e}")
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
        Обрабатываем ошибки для внутренних моделей.
        """
        try:
            # Получаем модель из данных запроса
            model = request_data.get('model', '')
            
            # Проверяем, что это ошибка для внутренней модели GigaChat
            if self._is_internal_gigachat_model(model, request_data):
                # Проверяем различные типы ошибок
                error_message = str(original_exception).lower()
                
                if ('401' in error_message or 
                    'unauthorized' in error_message or 
                    'authentication' in error_message or
                    'forbidden' in error_message or
                    'invalid' in error_message):
                    
                    logger.warning(f"Ошибка аутентификации для внутренней модели GigaChat {model}")
                    logger.debug(f"Ошибка: {original_exception}")
                    
                    # Логируем информацию о конфигурации для отладки
                    config_info = self.header_manager.get_configuration_info()
                    logger.debug(f"Конфигурация внутренней установки: {config_info}")
                
        except Exception as e:
            logger.error(f"Ошибка в async_post_call_failure_hook для внутренней модели: {e}")
    
    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        """
        Вызывается после успешного API запроса.
        Логируем успешные запросы к внутренним моделям.
        """
        try:
            model = data.get('model', '')
            if self._is_internal_gigachat_model(model, data):
                logger.debug(f"Успешный запрос к внутренней модели GigaChat {model}")
        except Exception as e:
            logger.error(f"Ошибка в async_post_call_success_hook для внутренней модели: {e}")
    
    def _is_internal_gigachat_model(self, model: str, kwargs: Dict[str, Any]) -> bool:
        """
        Проверяет, является ли модель внутренней моделью GigaChat
        """
        # Проверяем через header manager
        if self.header_manager.is_internal_model(model):
            return True
            
        # Дополнительная проверка по api_base
        api_base = kwargs.get('api_base', '')
        if 'litellm_params' in kwargs:
            api_base = kwargs['litellm_params'].get('api_base', api_base)
        
        internal_url = self.header_manager.get_internal_url()
        if internal_url and internal_url in api_base:
            return True
            
        return False


# Глобальный экземпляр callback
_internal_header_callback: Optional[InternalHeaderCallback] = None

def get_internal_header_callback() -> InternalHeaderCallback:
    """Получение глобального экземпляра InternalHeaderCallback"""
    global _internal_header_callback
    if _internal_header_callback is None:
        _internal_header_callback = InternalHeaderCallback()
    return _internal_header_callback

# Создаем экземпляр для использования в конфигурации
internal_header_callback_instance = get_internal_header_callback()

def setup_litellm_internal_gigachat_integration():
    """
    Настройка интеграции внутренней установки GigaChat с LiteLLM
    """
    import litellm
    
    # Добавляем callback в LiteLLM
    callback = get_internal_header_callback()
    
    # Проверяем, не добавлен ли уже callback
    if callback not in litellm.callbacks:
        litellm.callbacks.append(callback)
        logger.info("Internal GigaChat callback добавлен в LiteLLM")
    else:
        logger.debug("Internal GigaChat callback уже добавлен в LiteLLM")
