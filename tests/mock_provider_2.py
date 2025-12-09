#!/usr/bin/env python3
"""
Mock-сервер #2 для тестирования множественных прокси-провайдеров.

Порт: 8002
Модели: gpt-4-turbo, claude-3-opus
Auth: X-API-Key: test-token-provider2
"""

from flask import Flask, request, jsonify
import time
import uuid
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [PROVIDER2] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Конфигурация mock-сервера
PROVIDER_NAME = "Provider 2"
PORT = 8002
EXPECTED_AUTH_HEADER = "X-API-Key"
EXPECTED_AUTH_VALUE = "test-token-provider2"

# Список доступных моделей
AVAILABLE_MODELS = [
    {
        "id": "gp8989898-turbo",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "provider2"
    },
    {
        "id": "c90089opus",
        "object": "model",
        "created": int(time.time()),
        "owned_by": "provider2"
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
                    "content": f"[{PROVIDER_NAME}] Это ответ от модели {model}. Запрос обработан успешно!"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 15,
            "completion_tokens": 25,
            "total_tokens": 40
        }
    }
    
    logger.info("✓ Ответ сгенерирован")
    return jsonify(response), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "provider": PROVIDER_NAME}), 200


@app.before_request
def log_request():
    """Логирование всех входящих запросов."""
    logger.info(f"→ {request.method} {request.path}")


@app.after_request
def log_response(response):
    """Логирование всех исходящих ответов."""
    logger.info(f"← {response.status_code}")
    return response


if __name__ == '__main__':
    print("=" * 60)
    print(f"🚀 Mock {PROVIDER_NAME}")
    print("=" * 60)
    print(f"URL: http://localhost:{PORT}")
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
    
    app.run(host='0.0.0.0', port=PORT, debug=False)
