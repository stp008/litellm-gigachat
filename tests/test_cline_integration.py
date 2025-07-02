#!/usr/bin/env python3
"""
Тест интеграции с Cline - проверяет, что новый обработчик корректно работает
с запросами, похожими на те, что отправляет Cline
"""

import requests
import json
import time
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_cline_like_request():
    """Тестирует запрос, похожий на тот, что отправляет Cline"""
    
    # URL прокси-сервера
    proxy_url = "http://localhost:4000/v1/chat/completions"
    
    # Данные запроса в формате, который отправляет Cline
    request_data = {
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
                        "text": "Привет! Как дела? Можешь помочь с Python кодом?"
                    }
                ]
            }
        ],
        "temperature": 0,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer any-key"  # Токен управляется автоматически
    }
    
    try:
        logger.info("🚀 Отправляем тестовый запрос к GigaChat через прокси...")
        logger.info(f"URL: {proxy_url}")
        logger.info(f"Модель: {request_data['model']}")
        logger.info(f"Количество сообщений: {len(request_data['messages'])}")
        
        # Отправляем запрос
        response = requests.post(
            proxy_url,
            headers=headers,
            json=request_data,
            timeout=60
        )
        
        logger.info(f"📡 Получен ответ со статусом: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Проверяем структуру ответа
            if "choices" in result and len(result["choices"]) > 0:
                message_content = result["choices"][0]["message"]["content"]
                logger.info("✅ Запрос успешно обработан!")
                logger.info(f"📝 Ответ GigaChat: {message_content[:200]}...")
                
                # Проверяем, что ответ на русском языке (что указывает на корректную работу)
                if any(ord(char) > 127 for char in message_content):  # Проверка на кириллицу
                    logger.info("🇷🇺 Ответ содержит русские символы - интеграция работает корректно")
                
                return True
            else:
                logger.error("❌ Некорректная структура ответа")
                logger.error(f"Ответ: {result}")
                return False
        else:
            logger.error(f"❌ Ошибка HTTP {response.status_code}")
            logger.error(f"Ответ: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ Не удалось подключиться к прокси-серверу")
        logger.error("💡 Убедитесь, что прокси запущен: python3 start_proxy.py")
        return False
    except requests.exceptions.Timeout:
        logger.error("❌ Таймаут запроса")
        return False
    except Exception as e:
        logger.error(f"❌ Неожиданная ошибка: {e}")
        return False

def test_simple_request():
    """Тестирует простой запрос со строковым контентом"""
    
    proxy_url = "http://localhost:4000/v1/chat/completions"
    
    request_data = {
        "model": "gigachat",
        "messages": [
            {
                "role": "user",
                "content": "Привет! Как дела?"
            }
        ],
        "temperature": 0,
        "stream": False
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer any-key"
    }
    
    try:
        logger.info("🔄 Отправляем простой запрос...")
        
        response = requests.post(
            proxy_url,
            headers=headers,
            json=request_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            message_content = result["choices"][0]["message"]["content"]
            logger.info("✅ Простой запрос успешно обработан!")
            logger.info(f"📝 Ответ: {message_content[:100]}...")
            return True
        else:
            logger.error(f"❌ Ошибка простого запроса: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка простого запроса: {e}")
        return False

def main():
    """Основная функция тестирования"""
    
    print("🧪 Тестирование интеграции Cline с GigaChat")
    print("=" * 60)
    
    # Проверяем доступность прокси
    try:
        response = requests.get("http://localhost:4000/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Прокси-сервер доступен")
        else:
            logger.warning("⚠️ Прокси-сервер отвечает, но статус не 200")
    except:
        logger.error("❌ Прокси-сервер недоступен")
        logger.error("💡 Запустите прокси: python3 start_proxy.py")
        return False
    
    # Тестируем простой запрос
    logger.info("\n📋 Тест 1: Простой запрос")
    simple_success = test_simple_request()
    
    # Тестируем Cline-подобный запрос
    logger.info("\n📋 Тест 2: Cline-подобный запрос с массивами контента")
    cline_success = test_cline_like_request()
    
    # Результаты
    print("\n" + "=" * 60)
    print("📊 Результаты тестирования:")
    print(f"   🔹 Простой запрос: {'✅ Успех' if simple_success else '❌ Ошибка'}")
    print(f"   🔹 Cline-запрос: {'✅ Успех' if cline_success else '❌ Ошибка'}")
    
    if simple_success and cline_success:
        print("\n🎉 Все тесты пройдены! Интеграция с Cline работает корректно.")
        print("💡 Теперь вы можете использовать GigaChat через Cline без ошибок 'invalid JSON syntax'")
        return True
    else:
        print("\n⚠️ Некоторые тесты провалились. Проверьте логи выше.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
