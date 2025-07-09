import logging
from typing import Optional, Dict, Any, Literal
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from ..core.token_manager import get_global_token_manager

logger = logging.getLogger(__name__)

class GigaChatTokenCallback(CustomLogger):
    """
    Callback для LiteLLM Proxy, который автоматически обновляет токены GigaChat
    """
    
    def __init__(self):
        super().__init__()
        self.token_manager = get_global_token_manager()
        
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
        Автоматически обновляет токен для GigaChat моделей.
        """
        logger.debug("GigaChat async_pre_call_hook вызван")
        
        try:
            # Получаем модель из данных запроса
            model = data.get('model', '')
            logger.debug(f"Обрабатываем модель: {model}")
            
            # Проверяем, что это запрос к GigaChat
            if self._is_gigachat_model(model, data):
                logger.info(f"Обновляем токен для GigaChat модели: {model}")
                
                # Получаем актуальный токен
                current_token = self.token_manager.get_token()
                logger.debug(f"Получен токен: {current_token[:20]}...")
                
                # Обновляем api_key в данных запроса
                # В LiteLLM Proxy структура данных может быть разной
                if 'litellm_params' in data:
                    data['litellm_params']['api_key'] = current_token
                    logger.debug("Токен обновлен в litellm_params")
                else:
                    data['api_key'] = current_token
                    logger.debug("Токен обновлен в data")
                
                logger.debug(f"Токен успешно обновлен для модели {model}")
            else:
                logger.debug(f"Модель {model} не является GigaChat моделью")
                
        except Exception as e:
            logger.error(f"Ошибка при обновлении токена: {e}")
            # Не прерываем выполнение, позволяем LiteLLM попробовать с текущим токеном
        
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
        Обрабатываем ошибки авторизации.
        """
        try:
            # Получаем модель из данных запроса
            model = request_data.get('model', '')
            
            # Проверяем, что это ошибка авторизации для GigaChat
            if self._is_gigachat_model(model, request_data):
                # Проверяем различные типы ошибок авторизации
                error_message = str(original_exception).lower()
                
                if ('401' in error_message or 
                    'unauthorized' in error_message or 
                    'authentication' in error_message or
                    'invalid token' in error_message):
                    
                    logger.warning("Ошибка авторизации GigaChat, инвалидируем токен")
                    logger.debug(f"Ошибка: {original_exception}")
                    self.token_manager.invalidate_token()
                
        except Exception as e:
            logger.error(f"Ошибка в async_post_call_failure_hook: {e}")
    
    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        """
        Вызывается после успешного API запроса.
        Можно использовать для логирования успешных запросов.
        """
        try:
            model = data.get('model', '')
            if self._is_gigachat_model(model, data):
                logger.debug(f"Успешный запрос к GigaChat модели {model}")
        except Exception as e:
            logger.error(f"Ошибка в async_post_call_success_hook: {e}")
    
    def _is_gigachat_model(self, model: str, kwargs: Dict[str, Any]) -> bool:
        """
        Проверяет, является ли модель GigaChat моделью
        """
        # Проверяем по имени модели
        if 'gigachat' in model.lower():
            return True
            
        # Проверяем по api_base
        api_base = kwargs.get('api_base', '')
        if 'gigachat.devices.sberbank.ru' in api_base:
            return True
            
        return False


# Глобальный экземпляр callback
_gigachat_callback: Optional[GigaChatTokenCallback] = None

def get_gigachat_callback() -> GigaChatTokenCallback:
    """Получение глобального экземпляра GigaChatTokenCallback"""
    global _gigachat_callback
    if _gigachat_callback is None:
        _gigachat_callback = GigaChatTokenCallback()
    return _gigachat_callback

# Создаем экземпляр для использования в конфигурации
gigachat_callback_instance = get_gigachat_callback()

def setup_litellm_gigachat_integration():
    """
    Настройка интеграции GigaChat с LiteLLM
    """
    import litellm
    
    # Добавляем callback в LiteLLM
    callback = get_gigachat_callback()
    
    # Проверяем, не добавлен ли уже callback
    if callback not in litellm.callbacks:
        litellm.callbacks.append(callback)
        logger.info("GigaChat callback добавлен в LiteLLM")
    else:
        logger.debug("GigaChat callback уже добавлен в LiteLLM")
