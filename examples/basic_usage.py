#!/usr/bin/env python3
"""
Примеры использования GigaChat через LiteLLM с автоматическим обновлением токенов
"""

import os
import time
import logging
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import litellm
from src.core.token_manager import get_gigachat_token, get_global_token_manager
from src.callbacks.token_callback import setup_litellm_gigachat_integration

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def example_basic_chat():
    """Базовый пример чата с GigaChat"""
    logger.info("=== Базовый пример чата ===")
    
    setup_litellm_gigachat_integration()
    token = get_gigachat_token()
    
    response = litellm.completion(
        model="openai/GigaChat",
        api_base="https://gigachat.devices.sberbank.ru/api/v1",
        api_key=token,
        messages=[
            {"role": "user", "content": "Привет! Расскажи кратко о себе."}
        ]
    )
    
    print(f"Ответ: {response.choices[0].message.content}")
    print(f"Токены: {response.usage.total_tokens}")

def example_multiple_models():
    """Пример использования разных моделей GigaChat"""
    logger.info("=== Пример с разными моделями ===")
    
    setup_litellm_gigachat_integration()
    token = get_gigachat_token()
    
    models = [
        ("openai/GigaChat", "Базовая модель"),
        ("openai/GigaChat-Pro", "Pro модель"),
        ("openai/GigaChat-Max", "Max модель")
    ]
    
    question = "Что такое машинное обучение? Ответь кратко."
    
    for model, description in models:
        try:
            logger.info(f"Тестируем {description} ({model})")
            
            response = litellm.completion(
                model=model,
                api_base="https://gigachat.devices.sberbank.ru/api/v1",
                api_key=token,
                messages=[{"role": "user", "content": question}]
            )
            
            print(f"\n{description}:")
            print(f"Ответ: {response.choices[0].message.content[:200]}...")
            print(f"Токены: {response.usage.total_tokens}")
            
        except Exception as e:
            logger.error(f"Ошибка с моделью {model}: {e}")

def example_conversation():
    """Пример диалога с контекстом"""
    logger.info("=== Пример диалога с контекстом ===")
    
    setup_litellm_gigachat_integration()
    token = get_gigachat_token()
    
    messages = [
        {"role": "user", "content": "Привет! Меня зовут Алексей."},
    ]
    
    # Первый запрос
    response = litellm.completion(
        model="openai/GigaChat",
        api_base="https://gigachat.devices.sberbank.ru/api/v1",
        api_key=token,
        messages=messages
    )
    
    print(f"Пользователь: {messages[0]['content']}")
    print(f"GigaChat: {response.choices[0].message.content}")
    
    # Добавляем ответ в контекст
    messages.append({"role": "assistant", "content": response.choices[0].message.content})
    messages.append({"role": "user", "content": "Как меня зовут?"})
    
    # Второй запрос с контекстом
    response = litellm.completion(
        model="openai/GigaChat",
        api_base="https://gigachat.devices.sberbank.ru/api/v1",
        api_key=token,
        messages=messages
    )
    
    print(f"Пользователь: {messages[-1]['content']}")
    print(f"GigaChat: {response.choices[0].message.content}")

def example_token_management():
    """Пример управления токенами"""
    logger.info("=== Пример управления токенами ===")
    
    manager = get_global_token_manager()
    
    # Информация о токене
    info = manager.get_token_info()
    print(f"Есть токен: {info['has_token']}")
    print(f"Истекает через: {info['expires_in_seconds']} секунд")
    print(f"Токен истек: {info['is_expired']}")
    
    # Получение токена
    token = manager.get_token()
    print(f"Токен получен: {token[:20]}...")
    
    # Принудительное обновление
    new_token = manager.get_token(force_refresh=True)
    print(f"Новый токен: {new_token[:20]}...")
    
    # Инвалидация токена
    manager.invalidate_token()
    print("Токен инвалидирован")

def example_error_handling():
    """Пример обработки ошибок"""
    logger.info("=== Пример обработки ошибок ===")
    
    setup_litellm_gigachat_integration()
    
    try:
        # Попытка с неверным токеном
        response = litellm.completion(
            model="openai/GigaChat",
            api_base="https://gigachat.devices.sberbank.ru/api/v1",
            api_key="invalid_token",
            messages=[{"role": "user", "content": "Тест"}]
        )
    except Exception as e:
        logger.error(f"Ожидаемая ошибка с неверным токеном: {e}")
    
    try:
        # Правильный запрос
        token = get_gigachat_token()
        response = litellm.completion(
            model="openai/GigaChat",
            api_base="https://gigachat.devices.sberbank.ru/api/v1",
            api_key=token,
            messages=[{"role": "user", "content": "Привет!"}]
        )
        print(f"Успешный запрос: {response.choices[0].message.content}")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")

def example_streaming():
    """Пример потокового ответа"""
    logger.info("=== Пример потокового ответа ===")
    
    setup_litellm_gigachat_integration()
    token = get_gigachat_token()
    
    try:
        response = litellm.completion(
            model="openai/GigaChat",
            api_base="https://gigachat.devices.sberbank.ru/api/v1",
            api_key=token,
            messages=[{"role": "user", "content": "Расскажи короткую историю про кота"}],
            stream=True
        )
        
        print("Потоковый ответ:")
        for chunk in response:
            if chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end='', flush=True)
        print("\n")
        
    except Exception as e:
        logger.error(f"Ошибка потокового ответа: {e}")

def example_with_parameters():
    """Пример с различными параметрами"""
    logger.info("=== Пример с параметрами ===")
    
    setup_litellm_gigachat_integration()
    token = get_gigachat_token()
    
    # Креативный ответ
    response = litellm.completion(
        model="openai/GigaChat",
        api_base="https://gigachat.devices.sberbank.ru/api/v1",
        api_key=token,
        messages=[{"role": "user", "content": "Придумай название для стартапа в сфере AI"}],
        temperature=0.9,
        max_tokens=100
    )
    
    print(f"Креативный ответ (temperature=0.9): {response.choices[0].message.content}")
    
    # Консервативный ответ
    response = litellm.completion(
        model="openai/GigaChat",
        api_base="https://gigachat.devices.sberbank.ru/api/v1",
        api_key=token,
        messages=[{"role": "user", "content": "Что такое 2+2?"}],
        temperature=0.1,
        max_tokens=50
    )
    
    print(f"Консервативный ответ (temperature=0.1): {response.choices[0].message.content}")

def example_load_test():
    """Пример нагрузочного тестирования"""
    logger.info("=== Нагрузочное тестирование ===")
    
    setup_litellm_gigachat_integration()
    
    questions = [
        "Что такое Python?",
        "Расскажи о машинном обучении",
        "Как работает интернет?",
        "Что такое блокчейн?",
        "Объясни квантовые компьютеры"
    ]
    
    start_time = time.time()
    
    for i, question in enumerate(questions, 1):
        try:
            token = get_gigachat_token()  # Автоматически обновится при необходимости
            
            response = litellm.completion(
                model="openai/GigaChat",
                api_base="https://gigachat.devices.sberbank.ru/api/v1",
                api_key=token,
                messages=[{"role": "user", "content": question}]
            )
            
            logger.info(f"Запрос {i}/{len(questions)} выполнен успешно")
            
        except Exception as e:
            logger.error(f"Ошибка в запросе {i}: {e}")
    
    end_time = time.time()
    logger.info(f"Нагрузочное тестирование завершено за {end_time - start_time:.2f} секунд")

def main():
    """Главная функция с меню примеров"""
    
    # Проверка переменной окружения
    if not os.environ.get("GIGACHAT_AUTH_KEY"):
        logger.error("Установите переменную окружения GIGACHAT_AUTH_KEY")
        return
    
    examples = {
        "1": ("Базовый чат", example_basic_chat),
        "2": ("Разные модели", example_multiple_models),
        "3": ("Диалог с контекстом", example_conversation),
        "4": ("Управление токенами", example_token_management),
        "5": ("Обработка ошибок", example_error_handling),
        "6": ("Потоковый ответ", example_streaming),
        "7": ("Параметры запроса", example_with_parameters),
        "8": ("Нагрузочное тестирование", example_load_test),
        "9": ("Все примеры", None)
    }
    
    print("Выберите пример для запуска:")
    for key, (name, _) in examples.items():
        print(f"{key}. {name}")
    
    choice = input("\nВведите номер примера (или Enter для всех): ").strip()
    
    if not choice:
        choice = "9"
    
    if choice == "9":
        # Запуск всех примеров
        for key, (name, func) in examples.items():
            if func:
                print(f"\n{'='*60}")
                print(f"Запуск: {name}")
                print('='*60)
                try:
                    func()
                except Exception as e:
                    logger.error(f"Ошибка в примере '{name}': {e}")
                time.sleep(2)  # Пауза между примерами
    elif choice in examples:
        name, func = examples[choice]
        if func:
            print(f"\nЗапуск примера: {name}")
            func()
        else:
            print("Неверный выбор")
    else:
        print("Неверный номер примера")

if __name__ == "__main__":
    main()
