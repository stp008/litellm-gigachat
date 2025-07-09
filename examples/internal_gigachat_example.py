#!/usr/bin/env python3
"""
Пример использования внутренней установки GigaChat

Этот пример демонстрирует, как настроить и использовать внутреннюю установку GigaChat
с кастомным URL и заголовком аутентификации.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_internal_gigachat_environment():
    """
    Настройка переменных окружения для внутренней установки GigaChat
    """
    print("🔧 Настройка переменных окружения для внутренней установки GigaChat...")
    
    # Настройки внутренней установки
    os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
    os.environ['GIGACHAT_INTERNAL_URL'] = 'https://my-gigachat.company.com/api/v1'
    os.environ['GIGACHAT_AUTH_HEADER_NAME'] = 'X-Client-Id'
    os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'bddcba1a-6139-4b5f-9994-90f1b74e9109'
    os.environ['GIGACHAT_INTERNAL_MODEL_SUFFIX'] = 'internal'
    
    print("✅ Переменные окружения настроены:")
    print(f"   URL: {os.environ['GIGACHAT_INTERNAL_URL']}")
    print(f"   Header: {os.environ['GIGACHAT_AUTH_HEADER_NAME']}")
    print(f"   Suffix: {os.environ['GIGACHAT_INTERNAL_MODEL_SUFFIX']}")

def test_internal_header_manager():
    """
    Тестирование InternalHeaderManager
    """
    print("\n📋 Тестирование InternalHeaderManager...")
    
    from litellm_gigachat.core.internal_header_manager import (
        InternalHeaderManager,
        get_global_internal_header_manager,
        get_internal_auth_headers,
        is_internal_gigachat_enabled
    )
    
    # Создаем менеджер
    manager = InternalHeaderManager()
    
    # Проверяем конфигурацию
    print(f"✅ Внутренняя установка включена: {manager.is_enabled()}")
    print(f"✅ URL: {manager.get_internal_url()}")
    print(f"✅ Заголовки: {manager.get_auth_headers()}")
    print(f"✅ Доступные модели: {manager.get_model_names()}")
    
    # Проверяем валидацию
    is_valid = manager.validate_configuration()
    print(f"✅ Конфигурация валидна: {is_valid}")
    
    if not is_valid:
        print("❌ Ошибка: конфигурация невалидна!")
        return False
    
    # Тестируем определение моделей
    test_models = [
        ('gigachat-internal', True),
        ('gigachat-pro-internal', True),
        ('gigachat-max-internal', True),
        ('gigachat', False),
        ('gpt-4', False)
    ]
    
    print("\n🔍 Тестирование определения внутренних моделей:")
    for model, expected in test_models:
        result = manager.is_internal_model(model)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {model}: {result} (ожидалось: {expected})")
    
    return True

def test_internal_header_callback():
    """
    Тестирование InternalHeaderCallback
    """
    print("\n🔄 Тестирование InternalHeaderCallback...")
    
    from litellm_gigachat.callbacks.internal_header_callback import (
        InternalHeaderCallback,
        get_internal_header_callback
    )
    
    # Создаем callback
    callback = InternalHeaderCallback()
    
    # Тестируем определение внутренних моделей
    test_cases = [
        ('gigachat-internal', {}, True),
        ('gigachat-pro-internal', {}, True),
        ('gigachat', {}, False),
        ('some-model', {'api_base': 'https://my-gigachat.company.com/api/v1'}, True),
        ('some-model', {'api_base': 'https://other.example.com'}, False)
    ]
    
    print("🔍 Тестирование определения внутренних моделей в callback:")
    for model, kwargs, expected in test_cases:
        result = callback._is_internal_gigachat_model(model, kwargs)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {model} ({kwargs}): {result} (ожидалось: {expected})")
    
    return True

def demonstrate_openai_usage():
    """
    Демонстрация использования через OpenAI API
    """
    print("\n🌐 Демонстрация использования через OpenAI API...")
    print("📝 Пример кода для использования внутренних моделей:")
    
    example_code = '''
import openai

# Настройка клиента для работы с прокси
client = openai.OpenAI(
    base_url="http://localhost:4000",  # URL прокси-сервера
    api_key="any-key"                  # Любой ключ, заголовки управляются автоматически
)

# Использование внутренней модели
response = client.chat.completions.create(
    model="gigachat-internal",  # Внутренняя модель
    messages=[
        {"role": "user", "content": "Привет! Как дела?"}
    ]
)

print(response.choices[0].message.content)
'''
    
    print(example_code)

def demonstrate_litellm_usage():
    """
    Демонстрация использования через LiteLLM
    """
    print("\n⚡ Демонстрация использования через LiteLLM...")
    print("📝 Пример кода для прямого использования LiteLLM:")
    
    example_code = '''
import litellm
from litellm_gigachat import setup_litellm_internal_gigachat_integration

# Настройка интеграции
setup_litellm_internal_gigachat_integration()

# Использование внутренней модели
response = litellm.completion(
    model="openai/GigaChat",
    api_base="https://my-gigachat.company.com/api/v1",  # Будет заменен автоматически
    api_key="none",                                      # Не используется
    messages=[{"role": "user", "content": "Привет!"}],
    extra_headers={"X-Client-Id": "your-client-id"}     # Добавится автоматически
)

print(response.choices[0].message.content)
'''
    
    print(example_code)

def show_configuration_info():
    """
    Показать информацию о конфигурации
    """
    print("\n📊 Информация о конфигурации внутренней установки:")
    
    from litellm_gigachat.core.internal_header_manager import get_global_internal_header_manager
    
    manager = get_global_internal_header_manager()
    config_info = manager.get_configuration_info()
    
    print("🔧 Текущая конфигурация:")
    for key, value in config_info.items():
        if key == 'has_header_value':
            value_str = "✅ Установлен" if value else "❌ Не установлен"
        elif key == 'is_valid':
            value_str = "✅ Валидна" if value else "❌ Невалидна"
        elif key == 'enabled':
            value_str = "✅ Включена" if value else "❌ Отключена"
        else:
            value_str = str(value)
        
        print(f"   {key}: {value_str}")

def show_proxy_startup_instructions():
    """
    Показать инструкции по запуску прокси-сервера
    """
    print("\n🚀 Инструкции по запуску прокси-сервера:")
    print("=" * 60)
    
    print("1. Убедитесь, что переменные окружения настроены:")
    print("   export GIGACHAT_INTERNAL_ENABLED=true")
    print("   export GIGACHAT_INTERNAL_URL=https://my-gigachat.company.com/api/v1")
    print("   export GIGACHAT_AUTH_HEADER_NAME=X-Client-Id")
    print("   export GIGACHAT_AUTH_HEADER_VALUE=bddcba1a-6139-4b5f-9994-90f1b74e9109")
    print("   export GIGACHAT_INTERNAL_MODEL_SUFFIX=internal")
    
    print("\n2. Запустите прокси-сервер:")
    print("   litellm-gigachat")
    print("   # или")
    print("   python tools/start_proxy.py")
    
    print("\n3. Доступные модели:")
    print("   - gigachat-internal")
    print("   - gigachat-pro-internal")
    print("   - gigachat-max-internal")
    
    print("\n4. Тестирование через curl:")
    curl_example = '''curl -X POST http://localhost:4000/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "Authorization: Bearer any-key" \\
  -d '{
    "model": "gigachat-internal",
    "messages": [{"role": "user", "content": "Привет!"}]
  }'
'''
    print(curl_example)

def main():
    """
    Основная функция демонстрации
    """
    print("🎯 Демонстрация внутренней установки GigaChat")
    print("=" * 60)
    
    # Загружаем переменные окружения из .env файла
    load_dotenv()
    
    # Настраиваем окружение для демонстрации
    setup_internal_gigachat_environment()
    
    # Тестируем компоненты
    success = True
    success &= test_internal_header_manager()
    success &= test_internal_header_callback()
    
    # Показываем информацию о конфигурации
    show_configuration_info()
    
    # Демонстрируем использование
    demonstrate_openai_usage()
    demonstrate_litellm_usage()
    
    # Показываем инструкции по запуску
    show_proxy_startup_instructions()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Демонстрация завершена успешно!")
        print("🎉 Внутренняя установка GigaChat готова к использованию!")
    else:
        print("❌ Обнаружены ошибки в конфигурации")
        print("🔧 Проверьте настройки переменных окружения")
    
    print("\n📚 Дополнительная информация:")
    print("   - Документация: README.md")
    print("   - Примеры: examples/")
    print("   - Тесты: tests/test_internal_gigachat.py")

if __name__ == "__main__":
    main()
