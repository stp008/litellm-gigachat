import logging
from typing import Any, Dict, List, Union, Optional
from litellm.integrations.custom_logger import CustomLogger
from litellm.proxy.proxy_server import UserAPIKeyAuth, DualCache
from typing import Literal
import json
import uuid
import time

logger = logging.getLogger(__name__)

class GigaChatTransformer(CustomLogger):
    """
    Двунаправленный трансформер для обеспечения совместимости между OpenAI API и GigaChat API:
    
    Трансформация запросов (OpenAI → GigaChat):
    - Преобразует массивы фрагментов контента в строки
    - Трансформирует tools в functions
    - Преобразует tool_choice в function_call
    - Адаптирует параметры запроса
    
    Трансформация ответов (GigaChat → OpenAI):
    - Преобразует function_call в tool_calls
    - Адаптирует структуру ответа
    - Обрабатывает finish_reason
    - Поддерживает streaming
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

    def _transform_tools_to_functions(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Преобразует OpenAI tools в GigaChat functions"""
        try:
            if not tools:
                return []
            
            functions = []
            for tool in tools:
                if tool.get('type') == 'function' and 'function' in tool:
                    function_def = tool['function']
                    gigachat_function = {
                        'name': function_def.get('name'),
                        'description': function_def.get('description'),
                        'parameters': function_def.get('parameters', {})
                    }
                    functions.append(gigachat_function)
                    
            if self.debug_mode:
                logger.debug(f"Преобразовано {len(tools)} tools в {len(functions)} functions")
                
            return functions
        except Exception as e:
            logger.error(f"Ошибка при преобразовании tools в functions: {e}")
            return []

    def _transform_tool_choice_to_function_call(self, tool_choice: Union[str, Dict[str, Any]]) -> Union[str, Dict[str, Any]]:
        """Преобразует OpenAI tool_choice в GigaChat function_call"""
        try:
            if tool_choice == "none":
                return "none"
            elif tool_choice == "auto":
                return "auto"
            elif isinstance(tool_choice, dict) and tool_choice.get('type') == 'function':
                function_name = tool_choice.get('function', {}).get('name')
                if function_name:
                    return {'name': function_name}
            
            if self.debug_mode:
                logger.debug(f"Преобразован tool_choice: {tool_choice}")
                
            return tool_choice
        except Exception as e:
            logger.error(f"Ошибка при преобразовании tool_choice: {e}")
            return tool_choice

    def _prepare_gigachat_payload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Подготавливает полный payload для GigaChat API"""
        try:
            # Базовые параметры
            payload = {
                'model': data.get('model', 'GigaChat'),
                'messages': data.get('messages', []),
                'temperature': data.get('temperature'),
                'max_tokens': data.get('max_tokens'),
                'top_p': data.get('top_p'),
                'stream': data.get('stream', False)
            }

            # Обрабатываем tools (функции)
            tools = data.get('tools')
            if tools:
                functions = self._transform_tools_to_functions(tools)
                if functions:
                    payload['functions'] = functions

            # Обрабатываем tool_choice
            tool_choice = data.get('tool_choice')
            if tool_choice and tool_choice != "none":
                function_call = self._transform_tool_choice_to_function_call(tool_choice)
                payload['function_call'] = function_call

            # Удаляем значения None
            payload = {k: v for k, v in payload.items() if v is not None}
            
            if self.debug_mode:
                logger.debug(f"Подготовлен GigaChat payload с {len(payload)} параметрами")
                
            return payload
        except Exception as e:
            logger.error(f"Ошибка при подготовке GigaChat payload: {e}")
            return data

    def _transform_function_call_to_tool_calls(self, function_call: Any) -> List[Dict[str, Any]]:
        """Преобразует GigaChat function_call в OpenAI tool_calls"""
        try:
            if not function_call:
                return []
            
            # Получаем name и arguments из объекта (может быть dict или объект с атрибутами)
            if isinstance(function_call, dict):
                name = function_call.get('name', '')
                arguments = function_call.get('arguments', {})
            else:
                # Для объектов (включая Mock) используем getattr
                name = getattr(function_call, 'name', '')
                arguments = getattr(function_call, 'arguments', {})
            
            if not name:
                return []
            
            tool_call = {
                'id': f"call_{uuid.uuid4()}",
                'type': 'function',
                'function': {
                    'name': name,
                    'arguments': json.dumps(arguments, ensure_ascii=False)
                }
            }
            
            if self.debug_mode:
                logger.debug(f"Преобразован function_call в tool_calls: {name}")
                
            return [tool_call]
        except Exception as e:
            logger.error(f"Ошибка при преобразовании function_call в tool_calls: {e}")
            return []

    def _transform_gigachat_response_to_openai(self, giga_response: Any) -> Dict[str, Any]:
        """Преобразует ответ GigaChat в формат OpenAI"""
        try:
            if not hasattr(giga_response, 'choices') or not giga_response.choices:
                logger.warning("GigaChat ответ не содержит choices")
                return {}
            
            choice = giga_response.choices[0]
            message = choice.message
            usage = getattr(giga_response, "usage", None)

            openai_message = {
                "role": message.role,
                "content": message.content
            }

            finish_reason = "stop"

            # Обрабатываем function_call если есть
            function_call = getattr(message, "function_call", None)
            if function_call is not None:
                # Проверяем, что это не пустой Mock или объект
                if hasattr(function_call, 'name') and function_call.name:
                    tool_calls = self._transform_function_call_to_tool_calls(function_call)
                    if tool_calls:
                        openai_message["tool_calls"] = tool_calls
                        openai_message["content"] = None
                        finish_reason = "tool_calls"

            openai_response = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": getattr(giga_response, 'model', 'gpt-4'),
                "choices": [{
                    "index": 0,
                    "message": openai_message,
                    "finish_reason": finish_reason
                }],
                "usage": {
                    "prompt_tokens": usage.prompt_tokens if usage else 0,
                    "completion_tokens": usage.completion_tokens if usage else 0,
                    "total_tokens": usage.total_tokens if usage else 0
                },
                "system_fingerprint": None
            }
            
            if self.debug_mode:
                logger.debug(f"Преобразован GigaChat ответ в OpenAI формат")
                
            return openai_response
        except Exception as e:
            logger.error(f"Ошибка при преобразовании GigaChat ответа: {e}")
            return {}

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
        Трансформация запроса OpenAI → GigaChat перед отправкой
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
            
            # 1. Обрабатываем сообщения (преобразование контента)
            converted_count = self._process_messages(processed_data)
            
            # 2. Подготавливаем полный GigaChat payload (включая tools/functions)
            gigachat_payload = self._prepare_gigachat_payload(processed_data)
            
            # Обновляем данные запроса
            processed_data.update(gigachat_payload)
            
            # Логируем результаты
            self._log_request_info(processed_data, converted_count)
            
            if converted_count > 0:
                logger.info(f"Преобразовано {converted_count} сообщений для GigaChat API")
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Критическая ошибка в GigaChatTransformer: {e}")
            self.conversion_stats['errors'] += 1
            # Возвращаем оригинальные данные при ошибке
            return data

    async def async_post_call_success_hook(
        self,
        data: dict,
        user_api_key_dict: UserAPIKeyAuth,
        response,
    ):
        """
        Трансформация ответа GigaChat → OpenAI после успешного запроса
        """
        try:
            # Проверяем, является ли это ответом от GigaChat
            if not self._is_gigachat_request(data):
                if self.debug_mode:
                    logger.debug("Ответ не от GigaChat, пропускаем трансформацию")
                return response
            
            if self.debug_mode:
                logger.debug("Трансформируем ответ GigaChat в формат OpenAI")
            
            # Трансформируем ответ
            openai_response = self._transform_gigachat_response_to_openai(response)
            
            if openai_response:
                if self.debug_mode:
                    logger.debug("Ответ успешно трансформирован в OpenAI формат")
                return openai_response
            else:
                logger.warning("Не удалось трансформировать ответ, возвращаем оригинал")
                return response
                
        except Exception as e:
            logger.error(f"Ошибка при трансформации ответа GigaChat: {e}")
            # Возвращаем оригинальный ответ при ошибке
            return response

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
_gigachat_transformer = None

def get_gigachat_transformer(debug_mode: bool = True) -> GigaChatTransformer:
    """Получение глобального экземпляра GigaChatTransformer"""
    global _gigachat_transformer
    if _gigachat_transformer is None:
        _gigachat_transformer = GigaChatTransformer(debug_mode=debug_mode)
    return _gigachat_transformer

# Экземпляр для подключения в конфиге
gigachat_transformer_instance = get_gigachat_transformer()

def setup_gigachat_transformer():
    """
    Настройка интеграции GigaChatTransformer с LiteLLM
    """
    import litellm
    
    transformer = get_gigachat_transformer()
    
    # Проверяем, не добавлен ли уже transformer
    if transformer not in litellm.callbacks:
        litellm.callbacks.append(transformer)
        logger.info("GigaChatTransformer добавлен в LiteLLM")
    else:
        logger.debug("GigaChatTransformer уже добавлен в LiteLLM")

# Функция для получения статистики (для отладки)
def get_gigachat_transformer_stats() -> Dict[str, Any]:
    """Получить статистику работы трансформера"""
    transformer = get_gigachat_transformer()
    return transformer.get_stats()
