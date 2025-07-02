import logging
from typing import Any, Dict, List, Union, Optional
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from typing import Literal
import json

logger = logging.getLogger(__name__)

class FlattenContentHandler(CustomLogger):
    """
    Улучшенный обработчик для преобразования контента сообщений:
    - Преобразует массивы фрагментов контента в строки для GigaChat API
    - Обрабатывает сложные структуры данных
    - Обеспечивает надежную валидацию и обработку ошибок
    - Поддерживает детальное логирование для отладки
    """

    def __init__(self, debug_mode: bool = True):
        super().__init__()
        self.debug_mode = debug_mode
        self.processed_requests = 0
        self.conversion_stats = {
            'total_messages': 0,
            'converted_messages': 0,
            'errors': 0
        }

    def _is_gigachat_request(self, data: Dict[str, Any]) -> bool:
        """Проверяет, является ли запрос запросом к GigaChat"""
        try:
            model = data.get('model', '').lower()
            api_base = data.get('api_base', '').lower()
            litellm_params = data.get('litellm_params', {})
            
            # Проверяем по модели
            if 'gigachat' in model:
                return True
                
            # Проверяем по api_base
            if 'gigachat.devices.sberbank.ru' in api_base:
                return True
                
            # Проверяем в litellm_params
            if isinstance(litellm_params, dict):
                litellm_model = litellm_params.get('model', '').lower()
                litellm_api_base = litellm_params.get('api_base', '').lower()
                
                if 'gigachat' in litellm_model or 'gigachat.devices.sberbank.ru' in litellm_api_base:
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Ошибка при проверке типа запроса: {e}")
            return False

    def _validate_message_structure(self, message: Any) -> bool:
        """Валидирует структуру сообщения"""
        try:
            if not isinstance(message, dict):
                return False
            
            if 'role' not in message:
                return False
                
            if 'content' not in message:
                return False
                
            return True
        except Exception:
            return False

    def _extract_text_from_content_item(self, item: Any) -> str:
        """Извлекает текст из элемента контента"""
        try:
            if isinstance(item, str):
                return item
            elif isinstance(item, dict):
                # Обрабатываем разные типы контента
                if 'text' in item:
                    return str(item['text'])
                elif 'type' in item and item['type'] == 'text' and 'text' in item:
                    return str(item['text'])
                elif 'type' in item and item['type'] == 'image_url':
                    # Для изображений возвращаем описание или пустую строку
                    return f"[Image: {item.get('image_url', {}).get('url', 'unknown')}]"
                else:
                    # Пытаемся преобразовать весь объект в строку
                    return str(item)
            else:
                return str(item)
        except Exception as e:
            logger.warning(f"Не удалось извлечь текст из элемента контента: {e}")
            return str(item) if item is not None else ""

    def _flatten_content_array(self, content_array: List[Any]) -> str:
        """Преобразует массив контента в строку"""
        try:
            if not content_array:
                return ""
            
            text_parts = []
            for item in content_array:
                text_part = self._extract_text_from_content_item(item)
                if text_part:
                    text_parts.append(text_part)
            
            result = "".join(text_parts)
            
            if self.debug_mode:
                logger.debug(f"Преобразован массив из {len(content_array)} элементов в строку длиной {len(result)} символов")
            
            return result
        except Exception as e:
            logger.error(f"Ошибка при преобразовании массива контента: {e}")
            # Fallback: пытаемся преобразовать весь массив в строку
            try:
                return str(content_array)
            except:
                return ""

    def _process_message_content(self, message: Dict[str, Any]) -> bool:
        """Обрабатывает контент сообщения. Возвращает True, если было изменение"""
        try:
            content = message.get('content')
            
            if content is None:
                return False
            
            # Если контент уже строка, ничего не делаем
            if isinstance(content, str):
                return False
            
            # Если контент - массив, преобразуем в строку
            if isinstance(content, list):
                flattened_content = self._flatten_content_array(content)
                message['content'] = flattened_content
                
                if self.debug_mode:
                    logger.debug(f"Сообщение с ролью '{message.get('role', 'unknown')}': массив контента преобразован в строку")
                
                return True
            
            # Если контент - другой тип, пытаемся преобразовать в строку
            if not isinstance(content, str):
                message['content'] = str(content)
                logger.warning(f"Контент неожиданного типа {type(content)} преобразован в строку")
                return True
            
            return False
        except Exception as e:
            logger.error(f"Ошибка при обработке контента сообщения: {e}")
            return False

    def _process_messages(self, data: Dict[str, Any]) -> int:
        """Обрабатывает все сообщения в запросе. Возвращает количество измененных сообщений"""
        try:
            messages = data.get('messages', [])
            if not isinstance(messages, list):
                logger.warning("Поле 'messages' не является массивом")
                return 0
            
            converted_count = 0
            
            for i, message in enumerate(messages):
                self.conversion_stats['total_messages'] += 1
                
                if not self._validate_message_structure(message):
                    logger.warning(f"Сообщение {i} имеет некорректную структуру")
                    continue
                
                if self._process_message_content(message):
                    converted_count += 1
                    self.conversion_stats['converted_messages'] += 1
            
            return converted_count
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщений: {e}")
            self.conversion_stats['errors'] += 1
            return 0

    def _log_request_info(self, data: Dict[str, Any], converted_count: int):
        """Логирует информацию о запросе"""
        try:
            if self.debug_mode:
                model = data.get('model', 'unknown')
                messages_count = len(data.get('messages', []))
                
                logger.info(f"GigaChat запрос обработан: модель={model}, сообщений={messages_count}, преобразовано={converted_count}")
                
                # Логируем первые несколько символов каждого сообщения для отладки
                for i, message in enumerate(data.get('messages', [])[:3]):  # Только первые 3 сообщения
                    content = message.get('content', '')
                    content_preview = content[:100] + '...' if len(content) > 100 else content
                    logger.debug(f"Сообщение {i} ({message.get('role', 'unknown')}): {content_preview}")
        except Exception as e:
            logger.error(f"Ошибка при логировании информации о запросе: {e}")

    async def async_pre_call_hook(
        self,
        user_api_key_dict: UserAPIKeyAuth,
        cache: DualCache,
        data: dict,
        call_type: Literal["completion", "text_completion", "embeddings",
                           "image_generation", "moderation", "audio_transcription"],
    ) -> dict:
        """
        Основной hook для преобразования контента перед отправкой запроса
        """
        try:
            self.processed_requests += 1
            
            # Проверяем, является ли это запросом к GigaChat
            if not self._is_gigachat_request(data):
                if self.debug_mode:
                    logger.debug("Запрос не к GigaChat, пропускаем обработку")
                return data
            
            if self.debug_mode:
                logger.debug(f"Обрабатываем GigaChat запрос #{self.processed_requests}")
            
            # Создаем копию данных для безопасной обработки
            processed_data = data.copy()
            
            # Обрабатываем сообщения
            converted_count = self._process_messages(processed_data)
            
            # Логируем результаты
            self._log_request_info(processed_data, converted_count)
            
            if converted_count > 0:
                logger.info(f"Преобразовано {converted_count} сообщений для GigaChat API")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Критическая ошибка в FlattenContentHandler: {e}")
            self.conversion_stats['errors'] += 1
            # Возвращаем оригинальные данные при ошибке
            return data

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику работы обработчика"""
        return {
            'processed_requests': self.processed_requests,
            'conversion_stats': self.conversion_stats.copy()
        }

    def reset_stats(self):
        """Сбрасывает статистику"""
        self.processed_requests = 0
        self.conversion_stats = {
            'total_messages': 0,
            'converted_messages': 0,
            'errors': 0
        }


# Глобальный экземпляр для подключения в конфиге
_flatten_content_handler = None

def get_flatten_content_handler(debug_mode: bool = True) -> FlattenContentHandler:
    """Получение глобального экземпляра FlattenContentHandler"""
    global _flatten_content_handler
    if _flatten_content_handler is None:
        _flatten_content_handler = FlattenContentHandler(debug_mode=debug_mode)
    return _flatten_content_handler

# Экземпляр для подключения в конфиге
flatten_content_handler_instance = get_flatten_content_handler()

def setup_flatten_content_integration():
    """
    Настройка интеграции улучшенного обработчика контента с LiteLLM
    """
    import litellm
    
    handler = get_flatten_content_handler()
    
    # Проверяем, не добавлен ли уже handler
    if handler not in litellm.callbacks:
        litellm.callbacks.append(handler)
        logger.info("FlattenContentHandler добавлен в LiteLLM")
    else:
        logger.debug("FlattenContentHandler уже добавлен в LiteLLM")

# Функция для получения статистики (для отладки)
def get_flatten_content_stats() -> Dict[str, Any]:
    """Получить статистику работы обработчика"""
    handler = get_flatten_content_handler()
    return handler.get_stats()
