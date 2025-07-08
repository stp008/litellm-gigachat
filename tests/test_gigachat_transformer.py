#!/usr/bin/env python3
"""
Тесты для GigaChatTransformer - проверка трансформации между OpenAI и GigaChat форматами
"""

import pytest
import json
import uuid
from unittest.mock import Mock, AsyncMock
from src.callbacks.content_handler import GigaChatTransformer


class TestGigaChatTransformer:
    """Тесты для GigaChatTransformer"""
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        self.transformer = GigaChatTransformer(debug_mode=True)
    
    def test_is_gigachat_request_by_model(self):
        """Тест определения GigaChat запроса по модели"""
        # Положительные случаи
        assert self.transformer._is_gigachat_request({'model': 'gigachat'})
        assert self.transformer._is_gigachat_request({'model': 'GigaChat-Pro'})
        assert self.transformer._is_gigachat_request({'model': 'gigachat-max'})
        
        # Отрицательные случаи
        assert not self.transformer._is_gigachat_request({'model': 'gpt-4'})
        assert not self.transformer._is_gigachat_request({'model': 'claude'})
    
    def test_is_gigachat_request_by_api_base(self):
        """Тест определения GigaChat запроса по api_base"""
        # Положительные случаи
        assert self.transformer._is_gigachat_request({
            'api_base': 'https://gigachat.devices.sberbank.ru/api/v1'
        })
        
        # Отрицательные случаи
        assert not self.transformer._is_gigachat_request({
            'api_base': 'https://api.openai.com/v1'
        })
    
    def test_flatten_content_array(self):
        """Тест преобразования массива контента в строку"""
        # Простой массив строк
        content_array = ["Hello", " ", "world"]
        result = self.transformer._flatten_content_array(content_array)
        assert result == "Hello world"
        
        # Массив объектов с текстом
        content_array = [
            {"type": "text", "text": "Hello"},
            {"type": "text", "text": " world"}
        ]
        result = self.transformer._flatten_content_array(content_array)
        assert result == "Hello world"
        
        # Смешанный массив
        content_array = [
            "Hello",
            {"type": "text", "text": " beautiful"},
            {"text": " world"}
        ]
        result = self.transformer._flatten_content_array(content_array)
        assert result == "Hello beautiful world"
    
    def test_process_message_content(self):
        """Тест обработки контента сообщения"""
        # Сообщение с массивом контента
        message = {
            "role": "user",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": " world"}
            ]
        }
        
        changed = self.transformer._process_message_content(message)
        assert changed is True
        assert message["content"] == "Hello world"
        
        # Сообщение со строковым контентом (не должно измениться)
        message = {
            "role": "user",
            "content": "Hello world"
        }
        
        changed = self.transformer._process_message_content(message)
        assert changed is False
        assert message["content"] == "Hello world"
    
    def test_transform_tools_to_functions(self):
        """Тест преобразования OpenAI tools в GigaChat functions"""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {"type": "string"}
                        }
                    }
                }
            }
        ]
        
        functions = self.transformer._transform_tools_to_functions(tools)
        
        assert len(functions) == 1
        assert functions[0]["name"] == "get_weather"
        assert functions[0]["description"] == "Get weather information"
        assert "parameters" in functions[0]
    
    def test_transform_tool_choice_to_function_call(self):
        """Тест преобразования tool_choice в function_call"""
        # auto
        result = self.transformer._transform_tool_choice_to_function_call("auto")
        assert result == "auto"
        
        # none
        result = self.transformer._transform_tool_choice_to_function_call("none")
        assert result == "none"
        
        # Конкретная функция
        tool_choice = {
            "type": "function",
            "function": {"name": "get_weather"}
        }
        result = self.transformer._transform_tool_choice_to_function_call(tool_choice)
        assert result == {"name": "get_weather"}
    
    def test_transform_function_call_to_tool_calls(self):
        """Тест преобразования function_call в tool_calls"""
        function_call = {
            "name": "get_weather",
            "arguments": {"location": "Moscow"}
        }
        
        tool_calls = self.transformer._transform_function_call_to_tool_calls(function_call)
        
        assert len(tool_calls) == 1
        tool_call = tool_calls[0]
        
        assert "id" in tool_call
        assert tool_call["type"] == "function"
        assert tool_call["function"]["name"] == "get_weather"
        
        # Проверяем, что arguments корректно сериализованы
        arguments = json.loads(tool_call["function"]["arguments"])
        assert arguments == {"location": "Moscow"}
    
    def test_prepare_gigachat_payload(self):
        """Тест подготовки payload для GigaChat"""
        data = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": 0.7,
            "max_tokens": 100,
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "test_func",
                        "description": "Test function"
                    }
                }
            ],
            "tool_choice": "auto"
        }
        
        payload = self.transformer._prepare_gigachat_payload(data)
        
        assert payload["model"] == "gpt-4"
        assert payload["temperature"] == 0.7
        assert payload["max_tokens"] == 100
        assert "functions" in payload
        assert payload["function_call"] == "auto"
        assert len(payload["functions"]) == 1
    
    def test_transform_gigachat_response_to_openai(self):
        """Тест преобразования ответа GigaChat в формат OpenAI"""
        # Создаем mock ответа GigaChat
        mock_message = Mock()
        mock_message.role = "assistant"
        mock_message.content = "Hello, world!"
        mock_message.function_call = None
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 5
        mock_usage.total_tokens = 15
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        mock_response.model = "GigaChat"
        
        # Преобразуем ответ
        openai_response = self.transformer._transform_gigachat_response_to_openai(mock_response)
        
        assert "id" in openai_response
        assert openai_response["object"] == "chat.completion"
        assert "created" in openai_response
        assert openai_response["model"] == "GigaChat"
        
        choice = openai_response["choices"][0]
        assert choice["index"] == 0
        assert choice["message"]["role"] == "assistant"
        assert choice["message"]["content"] == "Hello, world!"
        assert choice["finish_reason"] == "stop"
        
        usage = openai_response["usage"]
        assert usage["prompt_tokens"] == 10
        assert usage["completion_tokens"] == 5
        assert usage["total_tokens"] == 15
    
    def test_transform_gigachat_response_with_function_call(self):
        """Тест преобразования ответа GigaChat с function_call"""
        # Создаем mock ответа GigaChat с function_call
        mock_function_call = Mock()
        mock_function_call.name = "get_weather"
        mock_function_call.arguments = {"location": "Moscow"}
        
        mock_message = Mock()
        mock_message.role = "assistant"
        mock_message.content = None
        mock_message.function_call = mock_function_call
        
        mock_choice = Mock()
        mock_choice.message = mock_message
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = None
        mock_response.model = "GigaChat"
        
        # Преобразуем ответ
        openai_response = self.transformer._transform_gigachat_response_to_openai(mock_response)
        
        choice = openai_response["choices"][0]
        assert choice["message"]["content"] is None
        assert choice["finish_reason"] == "tool_calls"
        assert "tool_calls" in choice["message"]
        
        tool_calls = choice["message"]["tool_calls"]
        assert len(tool_calls) == 1
        assert tool_calls[0]["function"]["name"] == "get_weather"
    
    @pytest.mark.asyncio
    async def test_async_pre_call_hook_non_gigachat(self):
        """Тест pre_call_hook для не-GigaChat запроса"""
        data = {"model": "gpt-4", "messages": []}
        
        result = await self.transformer.async_pre_call_hook(
            user_api_key_dict=Mock(),
            cache=Mock(),
            data=data,
            call_type="completion"
        )
        
        # Данные не должны измениться
        assert result == data
    
    @pytest.mark.asyncio
    async def test_async_pre_call_hook_gigachat(self):
        """Тест pre_call_hook для GigaChat запроса"""
        data = {
            "model": "gigachat",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Hello"},
                        {"type": "text", "text": " world"}
                    ]
                }
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {"name": "test_func"}
                }
            ]
        }
        
        result = await self.transformer.async_pre_call_hook(
            user_api_key_dict=Mock(),
            cache=Mock(),
            data=data,
            call_type="completion"
        )
        
        # Проверяем, что контент был преобразован
        assert result["messages"][0]["content"] == "Hello world"
        
        # Проверяем, что tools были преобразованы в functions
        assert "functions" in result
        assert len(result["functions"]) == 1
    
    def test_get_stats(self):
        """Тест получения статистики"""
        stats = self.transformer.get_stats()
        
        assert "processed_requests" in stats
        assert "conversion_stats" in stats
        assert stats["processed_requests"] == 0
    
    def test_reset_stats(self):
        """Тест сброса статистики"""
        # Увеличиваем счетчики
        self.transformer.processed_requests = 5
        self.transformer.conversion_stats["total_messages"] = 10
        
        # Сбрасываем
        self.transformer.reset_stats()
        
        # Проверяем
        assert self.transformer.processed_requests == 0
        assert self.transformer.conversion_stats["total_messages"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
