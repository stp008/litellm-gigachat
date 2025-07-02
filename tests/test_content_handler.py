#!/usr/bin/env python3
"""
Тесты для FlattenContentHandler
"""

import asyncio
import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict, Any
from src.callbacks.content_handler import FlattenContentHandler, get_flatten_content_handler

# Настройка логирования для тестов
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MockUserAPIKeyAuth:
    """Mock объект для тестирования"""
    pass

class MockDualCache:
    """Mock объект для тестирования"""
    pass

async def test_simple_string_content():
    """Тест: обычный строковый контент не должен изменяться"""
    print("\n=== Тест 1: Строковый контент ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    
    data = {
        "model": "gigachat",
        "messages": [
            {"role": "user", "content": "Привет, как дела?"}
        ]
    }
    
    result = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data, "completion"
    )
    
    assert result["messages"][0]["content"] == "Привет, как дела?"
    print("✅ Строковый контент остался без изменений")

async def test_array_content_conversion():
    """Тест: массив контента должен преобразовываться в строку"""
    print("\n=== Тест 2: Преобразование массива контента ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    
    data = {
        "model": "gigachat",
        "messages": [
            {
                "role": "system",
                "content": [
                    {"type": "text", "text": "Ты помощник по программированию. "},
                    {"type": "text", "text": "Отвечай кратко и по делу."}
                ]
            }
        ]
    }
    
    result = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data, "completion"
    )
    
    expected_content = "Ты помощник по программированию. Отвечай кратко и по делу."
    assert result["messages"][0]["content"] == expected_content
    print(f"✅ Массив преобразован в строку: '{expected_content}'")

async def test_complex_content_with_images():
    """Тест: сложный контент с изображениями"""
    print("\n=== Тест 3: Сложный контент с изображениями ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    
    data = {
        "model": "gigachat",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Что на этом изображении? "},
                    {
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABA..."}
                    },
                    {"type": "text", "text": " Опиши подробно."}
                ]
            }
        ]
    }
    
    result = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data, "completion"
    )
    
    content = result["messages"][0]["content"]
    assert "Что на этом изображении?" in content
    assert "[Image:" in content
    assert "Опиши подробно." in content
    print(f"✅ Сложный контент обработан: '{content[:100]}...'")

async def test_non_gigachat_request():
    """Тест: запросы не к GigaChat не должны обрабатываться"""
    print("\n=== Тест 4: Запрос не к GigaChat ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    
    data = {
        "model": "gpt-4",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Этот массив не должен изменяться"}
                ]
            }
        ]
    }
    
    result = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data, "completion"
    )
    
    # Контент должен остаться массивом
    assert isinstance(result["messages"][0]["content"], list)
    print("✅ Запрос не к GigaChat не обработан")

async def test_edge_cases():
    """Тест: граничные случаи"""
    print("\n=== Тест 5: Граничные случаи ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    
    # Пустой массив контента
    data1 = {
        "model": "gigachat",
        "messages": [
            {"role": "user", "content": []}
        ]
    }
    
    result1 = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data1, "completion"
    )
    
    assert result1["messages"][0]["content"] == ""
    print("✅ Пустой массив преобразован в пустую строку")
    
    # None контент
    data2 = {
        "model": "gigachat",
        "messages": [
            {"role": "user", "content": None}
        ]
    }
    
    result2 = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data2, "completion"
    )
    
    assert result2["messages"][0]["content"] is None
    print("✅ None контент остался без изменений")

async def test_statistics():
    """Тест: статистика работы"""
    print("\n=== Тест 6: Статистика ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    handler.reset_stats()
    
    # Обрабатываем несколько запросов
    for i in range(3):
        data = {
            "model": "gigachat",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": f"Сообщение {i}"}]
                }
            ]
        }
        
        await handler.async_pre_call_hook(
            MockUserAPIKeyAuth(), MockDualCache(), data, "completion"
        )
    
    stats = handler.get_stats()
    assert stats["processed_requests"] == 3
    assert stats["conversion_stats"]["total_messages"] == 3
    assert stats["conversion_stats"]["converted_messages"] == 3
    print(f"✅ Статистика корректна: {stats}")

async def test_cline_like_request():
    """Тест: запрос похожий на тот, что отправляет Cline"""
    print("\n=== Тест 7: Cline-подобный запрос ===")
    
    handler = FlattenContentHandler(debug_mode=True)
    
    # Имитируем запрос от Cline
    data = {
        "model": "gigachat",
        "messages": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "text",
                        "text": "You are Cline, a highly skilled software engineer with extensive knowledge in many programming languages, frameworks, design patterns, and best practices."
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Привет! Помоги мне с кодом."
                    }
                ]
            }
        ]
    }
    
    result = await handler.async_pre_call_hook(
        MockUserAPIKeyAuth(), MockDualCache(), data, "completion"
    )
    
    # Проверяем, что оба сообщения преобразованы в строки
    assert isinstance(result["messages"][0]["content"], str)
    assert isinstance(result["messages"][1]["content"], str)
    
    system_content = result["messages"][0]["content"]
    user_content = result["messages"][1]["content"]
    
    assert "You are Cline" in system_content
    assert "Привет! Помоги мне с кодом." in user_content
    
    print(f"✅ Cline-подобный запрос обработан корректно")
    print(f"   System: {system_content[:50]}...")
    print(f"   User: {user_content}")

async def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 Запуск тестов FlattenContentHandler")
    print("=" * 60)
    
    tests = [
        test_simple_string_content,
        test_array_content_conversion,
        test_complex_content_with_images,
        test_non_gigachat_request,
        test_edge_cases,
        test_statistics,
        test_cline_like_request
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ Тест {test.__name__} провален: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования:")
    print(f"   ✅ Пройдено: {passed}")
    print(f"   ❌ Провалено: {failed}")
    print(f"   📈 Успешность: {passed/(passed+failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 Все тесты пройдены успешно!")
        return True
    else:
        print(f"\n⚠️  {failed} тест(ов) провалено")
        return False

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
