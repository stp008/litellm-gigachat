#!/usr/bin/env python3
"""
Базовый тест функциональности проекта LiteLLM GigaChat
"""

import logging
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.litellm_gigachat.core import get_global_token_manager, get_gigachat_token
from src.litellm_gigachat.callbacks import get_gigachat_callback
import litellm

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def test_token_manager():
    """Тест TokenManager"""
    print("=== Тестирование TokenManager ===")
    
    try:
        manager = get_global_token_manager()
        print("✓ TokenManager инициализирован")
        
        token = manager.get_token()
        print(f"✓ Токен получен: {token[:20]}...")
        
        info = manager.get_token_info()
        print(f"✓ Информация о токене:")
        print(f"  - Есть токен: {info['has_token']}")
        print(f"  - Истекает через: {info['expires_in_seconds']:.0f} секунд")
        print(f"  - Истек: {info['is_expired']}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка TokenManager: {e}")
        return False

def test_callback():
    """Тест GigaChatTokenCallback"""
    print("\n=== Тестирование GigaChatTokenCallback ===")
    
    try:
        callback = get_gigachat_callback()
        print("✓ Callback инициализирован")
        
        # Тестируем определение GigaChat модели
        test_cases = [
            ('gigachat', {}, True),
            ('gigachat-pro', {}, True),
            ('gpt-4', {}, False),
            ('test', {'api_base': 'https://gigachat.devices.sberbank.ru/api/v1'}, True)
        ]
        
        for model, kwargs, expected in test_cases:
            is_gigachat = callback._is_gigachat_model(model, kwargs)
            status = "✓" if is_gigachat == expected else "✗"
            print(f"  {status} Модель '{model}': {'GigaChat' if is_gigachat else 'Не GigaChat'}")
            if is_gigachat != expected:
                return False
        
        return True
    except Exception as e:
        print(f"✗ Ошибка Callback: {e}")
        return False

def test_direct_api_call():
    """Тест прямого вызова GigaChat API"""
    print("\n=== Тестирование прямого вызова GigaChat API ===")
    
    try:
        token = get_gigachat_token()
        print(f"✓ Токен получен: {token[:20]}...")
        
        response = litellm.completion(
            model='openai/GigaChat',
            api_base='https://gigachat.devices.sberbank.ru/api/v1',
            api_key=token,
            messages=[{'role': 'user', 'content': 'Скажи "Тест пройден" одним словом'}],
            max_tokens=10
        )
        
        answer = response.choices[0].message.content.strip()
        print(f"✓ Запрос выполнен успешно!")
        print(f"✓ Ответ GigaChat: {answer}")
        
        return True
    except Exception as e:
        print(f"✗ Ошибка API вызова: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 Запуск базового тестирования LiteLLM GigaChat интеграции")
    print("=" * 60)
    
    tests = [
        ("TokenManager", test_token_manager),
        ("Callback", test_callback),
        ("Direct API", test_direct_api_call)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✓ {test_name}: ПРОЙДЕН")
            else:
                print(f"✗ {test_name}: ПРОВАЛЕН")
        except Exception as e:
            print(f"✗ {test_name}: ОШИБКА - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Результаты тестирования: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Проект готов к использованию.")
        return 0
    else:
        print("❌ Некоторые тесты провалены. Проверьте конфигурацию.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
