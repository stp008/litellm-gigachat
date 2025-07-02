#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы LiteLLM прокси с GigaChat
"""

import requests
import json

def test_proxy():
    """Тестирует работу прокси сервера"""
    
    # URL прокси сервера
    proxy_url = "http://localhost:4000/chat/completions"
    
    # Тестовый запрос
    payload = {
        "model": "gigachat",
        "messages": [
            {
                "role": "user", 
                "content": "Привет! Как дела?"
            }
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("Отправляем запрос к прокси серверу...")
        print(f"URL: {proxy_url}")
        print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
        
        response = requests.post(proxy_url, json=payload, headers=headers, timeout=30)
        
        print(f"\nСтатус ответа: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nУспешный ответ:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\nОшибка:")
            print(f"Текст ответа: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при выполнении запроса: {e}")
    except json.JSONDecodeError as e:
        print(f"Ошибка при парсинге JSON: {e}")
        print(f"Текст ответа: {response.text}")

if __name__ == "__main__":
    test_proxy()
