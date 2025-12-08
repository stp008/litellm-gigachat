#!/usr/bin/env python3
"""
Mock-сервер для тестирования прокси-провайдера.

Эмулирует OpenAI-совместимый API endpoint с кастомной аутентификацией.
Используется для локального тестирования функциональности прокси-провайдера.
"""

from flask import Flask, request, jsonify
import time
import uuid
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация mock-сервера
EXPECTED_AUTH_HEADER = "X-Client-Id"
EXPECTED_AUTH_VALUE = "test-client-id-12345"

# Список доступных моделей
AVAILABLE_MODELS = [
    {
        "id": "llama-3.1-70b",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "mock-provider"
    },
    {
        "id": "mistral-large",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "mock-provider"
    },
    {
        "id": "gpt-4-turbo",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "mock-provider"
    }
]


def check_auth():
    """Проверка аутентификации через заголовок."""
    auth_value = request.headers.get(EXPECTED_AUTH_HEADER)
    
    if not auth_value:
        logger.warning(f"❌ Отсутствует заголовок {EXPECTED_AUTH_HEADER}")
        return False, f"Missing {EXPECTED_AUTH_HEADER} header"
    
    if auth_value != EXPECTED_AUTH_VALUE:
        logger.warning(f"❌ Неверное значение заголовка: {auth_value}")
        return False, f"Invalid {EXPECTED_AUTH_HEADER} value"
    
    logger.info(f"✓ Аутентификация успешна")
    return True, None


@app.route('/v1/models', methods=['GET'])
def list_models():
    """Endpoint для получения списка моделей."""
    logger.info("📋 Запрос списка моделей")
    
    # Проверяем аутентификацию
    is_auth, error = check_auth()
    if not is_auth:
        return jsonify({"error": error}), 401
    
    response = {
        "object": "list",
        "data": AVAILABLE_MODELS
    }
    
    logger.info(f"✓ Возвращено {len(AVAILABLE_MODELS)} моделей")
    return jsonify(response), 200


@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Endpoint для генерации ответов."""
    logger.info("💬 Запрос генерации ответа")
    
    # Проверяем аутентификацию
    is_auth, error = check_auth()
    if not is_auth:
        return jsonify({"error": error}), 401
    
    # Получаем данные запроса
    data = request.get_json()
    model = data.get('model', 'unknown')
    messages = data.get('messages', [])
    
    logger.info(f"  Модель: {model}")
    logger.info(f"  Сообщений: {len(messages)}")
    
    # Формируем mock-ответ
    response = {
        "id": f"chatcmpl-{uuid.uuid4()}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": f"Это mock-ответ от модели {model}. Ваш запрос был успешно обработан!"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }
    
    logger.info("✓ Ответ сгенерирован")
    return jsonify(response), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok"}), 200


@app.before_request
def log_request():
    """Логирование всех входящих запросов."""
    logger.info(f"→ {request.method} {request.path}")
    logger.debug(f"  Headers: {dict(request.headers)}")


@app.after_request
def log_response(response):
    """Логирование всех исходящих ответов."""
    logger.info(f"← {response.status_code}")
    return response


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Mock Proxy Provider Server")
    print("=" * 60)
    print(f"URL: http://localhost:8000")
    print(f"Auth Header: {EXPECTED_AUTH_HEADER}")
    print(f"Auth Value: {EXPECTED_AUTH_VALUE}")
    print("=" * 60)
    print("\nEndpoints:")
    print("  GET  /v1/models              - Список моделей")
    print("  POST /v1/chat/completions    - Генерация ответов")
    print("  GET  /health                 - Health check")
    print("=" * 60)
    print("\nДоступные модели:")
    for model in AVAILABLE_MODELS:
        print(f"  - {model['id']}")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8000, debug=True)
