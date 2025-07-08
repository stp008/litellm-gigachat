#!/usr/bin/env python3
"""
Пример использования GigaChatTransformer для трансформации запросов и ответов
между форматами OpenAI и GigaChat API.
"""

import asyncio
import json
from unittest.mock import Mock
from src.callbacks.content_handler import GigaChatTransformer


async def example_request_transformation():
    """Пример трансформации запроса OpenAI → GigaChat"""
    print("=== Пример трансформации запроса OpenAI → GigaChat ===")
    
    transformer = GigaChatTransformer(debug_mode=True)
    
    # Пример OpenAI запроса с массивом контента и tools
    openai_request = {
        "model": "gigachat",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Привет! "},
                    {"type": "text", "text": "Какая погода в Москве?"}
                ]
            }
        ],
        "tools": [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "Получить информацию о погоде",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Город для получения погоды"
                            }
                        },
                        "required": ["location"]
                    }
                }
            }
        ],
        "tool_choice": "auto",
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    print("Исходный OpenAI запрос:")
    print(json.dumps(openai_request, indent=2, ensure_ascii=False))
    
    # Трансформируем запрос
    transformed_request = await transformer.async_pre_call_hook(
        user_api_key_dict=Mock(),
        cache=Mock(),
        data=openai_request,
        call_type="completion"
    )
    
    print("\nПреобразованный GigaChat запрос:")
    print(json.dumps(transformed_request, indent=2, ensure_ascii=False))
    
    return transformed_request


def example_response_transformation():
    """Пример трансформации ответа GigaChat → OpenAI"""
    print("\n=== Пример трансформации ответа GigaChat → OpenAI ===")
    
    transformer = GigaChatTransformer(debug_mode=True)
    
    # Создаем mock ответа GigaChat с function_call
    mock_function_call = Mock()
    mock_function_call.name = "get_weather"
    mock_function_call.arguments = {"location": "Москва"}
    
    mock_message = Mock()
    mock_message.role = "assistant"
    mock_message.content = None
    mock_message.function_call = mock_function_call
    
    mock_choice = Mock()
    mock_choice.message = mock_message
    
    mock_usage = Mock()
    mock_usage.prompt_tokens = 25
    mock_usage.completion_tokens = 10
    mock_usage.total_tokens = 35
    
    mock_gigachat_response = Mock()
    mock_gigachat_response.choices = [mock_choice]
    mock_gigachat_response.usage = mock_usage
    mock_gigachat_response.model = "GigaChat-Pro"
    
    print("Исходный GigaChat ответ (mock):")
    print(f"- model: {mock_gigachat_response.model}")
    print(f"- message.role: {mock_message.role}")
    print(f"- message.content: {mock_message.content}")
    print(f"- message.function_call.name: {mock_function_call.name}")
    print(f"- message.function_call.arguments: {mock_function_call.arguments}")
    print(f"- usage: {mock_usage.prompt_tokens}/{mock_usage.completion_tokens}/{mock_usage.total_tokens}")
    
    # Трансформируем ответ
    openai_response = transformer._transform_gigachat_response_to_openai(mock_gigachat_response)
    
    print("\nПреобразованный OpenAI ответ:")
    print(json.dumps(openai_response, indent=2, ensure_ascii=False))
    
    return openai_response


def example_content_flattening():
    """Пример преобразования массива контента в строку"""
    print("\n=== Пример преобразования массива контента ===")
    
    transformer = GigaChatTransformer(debug_mode=True)
    
    # Различные типы массивов контента
    test_cases = [
        # Простой массив строк
        ["Привет, ", "как дела?"],
        
        # Массив объектов с текстом
        [
            {"type": "text", "text": "Расскажи мне про "},
            {"type": "text", "text": "искусственный интеллект"}
        ],
        
        # Смешанный массив
        [
            "Вопрос: ",
            {"type": "text", "text": "Что такое "},
            {"text": "машинное обучение?"}
        ],
        
        # Массив с изображением
        [
            {"type": "text", "text": "Опиши это изображение: "},
            {"type": "image_url", "image_url": {"url": "https://example.com/image.jpg"}}
        ]
    ]
    
    for i, content_array in enumerate(test_cases, 1):
        print(f"\nТест {i}:")
        print(f"Исходный массив: {content_array}")
        
        flattened = transformer._flatten_content_array(content_array)
        print(f"Результат: '{flattened}'")


def example_tools_transformation():
    """Пример преобразования tools в functions"""
    print("\n=== Пример преобразования tools в functions ===")
    
    transformer = GigaChatTransformer(debug_mode=True)
    
    # OpenAI tools
    openai_tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Получить текущую погоду в указанном городе",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Название города"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "Единица измерения температуры"
                        }
                    },
                    "required": ["location"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculate",
                "description": "Выполнить математическое вычисление",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Математическое выражение для вычисления"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    ]
    
    print("Исходные OpenAI tools:")
    print(json.dumps(openai_tools, indent=2, ensure_ascii=False))
    
    # Преобразуем в GigaChat functions
    gigachat_functions = transformer._transform_tools_to_functions(openai_tools)
    
    print("\nПреобразованные GigaChat functions:")
    print(json.dumps(gigachat_functions, indent=2, ensure_ascii=False))


def example_stats():
    """Пример работы со статистикой"""
    print("\n=== Пример работы со статистикой ===")
    
    transformer = GigaChatTransformer(debug_mode=True)
    
    print("Начальная статистика:")
    stats = transformer.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Симулируем обработку нескольких запросов
    transformer.processed_requests = 5
    transformer.conversion_stats['total_messages'] = 12
    transformer.conversion_stats['converted_messages'] = 8
    transformer.conversion_stats['errors'] = 1
    
    print("\nСтатистика после обработки:")
    stats = transformer.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    # Сбрасываем статистику
    transformer.reset_stats()
    
    print("\nСтатистика после сброса:")
    stats = transformer.get_stats()
    print(json.dumps(stats, indent=2, ensure_ascii=False))


async def main():
    """Главная функция с примерами"""
    print("🚀 Примеры использования GigaChatTransformer")
    print("=" * 60)
    
    # Пример трансформации запроса
    await example_request_transformation()
    
    # Пример трансформации ответа
    example_response_transformation()
    
    # Пример преобразования контента
    example_content_flattening()
    
    # Пример преобразования tools
    example_tools_transformation()
    
    # Пример работы со статистикой
    example_stats()
    
    print("\n✅ Все примеры выполнены успешно!")


if __name__ == "__main__":
    asyncio.run(main())
