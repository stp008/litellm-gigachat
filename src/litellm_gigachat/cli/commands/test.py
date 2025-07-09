"""
Команда test для тестирования подключения к GigaChat.
"""

import click
import logging
import os
import sys
import time
from dotenv import load_dotenv

from ..utils import check_environment_variables
from ...core.token_manager import get_global_token_manager


logger = logging.getLogger(__name__)


def test_environment() -> bool:
    """Тестирование переменных окружения."""
    logger.info("Проверка переменных окружения...")
    
    env_vars = check_environment_variables()
    
    for var, status in env_vars.items():
        if "✓" in status:
            logger.info(f"  ✓ {var}: установлена")
        else:
            logger.error(f"  ✗ {var}: не установлена")
    
    # Проверяем обязательную переменную
    if "✗" in env_vars.get("GIGACHAT_AUTH_KEY", ""):
        logger.error("GIGACHAT_AUTH_KEY обязательна для работы")
        return False
    
    return True


def test_token_manager() -> bool:
    """Тестирование TokenManager."""
    logger.info("Тестирование TokenManager...")
    
    try:
        token_manager = get_global_token_manager()
        logger.debug(f"TokenManager type: {type(token_manager)}")
        
        # Получаем токен
        logger.info("  Получение токена...")
        start_time = time.time()
        token = token_manager.get_token()
        end_time = time.time()
        
        if token:
            logger.info(f"  ✓ Токен получен за {end_time - start_time:.2f}s")
            logger.debug(f"  Token preview: {token[:20]}...")
            
            # Проверяем информацию о токене
            token_info = token_manager.get_token_info()
            if token_info:
                logger.info(f"  ✓ Токен действителен до: {token_info.get('expires_at', 'unknown')}")
                logger.debug(f"  Token info: {token_info}")
            
            return True
        else:
            logger.error("  ✗ Не удалось получить токен")
            return False
            
    except Exception as exc:
        logger.error(f"  ✗ Ошибка TokenManager: {exc}")
        logger.debug("TokenManager error details:", exc_info=True)
        return False


def test_gigachat_api() -> bool:
    """Тестирование GigaChat API через прямой HTTP запрос."""
    logger.info("Тестирование GigaChat API...")
    
    try:
        import requests
        
        # Получаем токен
        token_manager = get_global_token_manager()
        token = token_manager.get_token()
        
        if not token:
            logger.error("  ✗ Не удалось получить токен для API")
            return False
        
        # Тестовый запрос
        logger.info("  Отправка тестового запроса...")
        start_time = time.time()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "GigaChat:latest",
            "messages": [{"role": "user", "content": "Привет! Это тестовое сообщение."}],
            "max_tokens": 100
        }
        
        response = requests.post(
            "https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"  ✓ API отвечает за {end_time - start_time:.2f}s")
            
            if result.get("choices"):
                content = result["choices"][0]["message"]["content"]
                logger.info(f"  ✓ Ответ получен: {content[:100]}...")
                logger.debug(f"  Full response: {result}")
                return True
            else:
                logger.error("  ✗ Некорректная структура ответа от API")
                logger.debug(f"  Response: {result}")
                return False
        else:
            logger.error(f"  ✗ API вернул ошибку: {response.status_code}")
            logger.debug(f"  Response: {response.text}")
            return False
            
    except Exception as exc:
        logger.error(f"  ✗ Ошибка GigaChat API: {exc}")
        logger.debug("GigaChat API error details:", exc_info=True)
        return False


def test_litellm_integration() -> bool:
    """Тестирование интеграции с LiteLLM."""
    logger.info("Тестирование интеграции с LiteLLM...")
    
    try:
        import litellm
        
        # Настраиваем LiteLLM для GigaChat
        logger.info("  Настройка LiteLLM...")
        
        # Получаем токен
        token_manager = get_global_token_manager()
        token = token_manager.get_token()
        
        if not token:
            logger.error("  ✗ Не удалось получить токен для LiteLLM")
            return False
        
        # Тестовый запрос через LiteLLM
        logger.info("  Отправка запроса через LiteLLM...")
        start_time = time.time()
        
        response = litellm.completion(
            model="gigachat/GigaChat:latest",
            messages=[{"role": "user", "content": "Тест LiteLLM интеграции"}],
            api_key=token,
            api_base="https://gigachat.devices.sberbank.ru/api/v1"
        )
        
        end_time = time.time()
        
        if response and response.choices:
            logger.info(f"  ✓ LiteLLM интеграция работает за {end_time - start_time:.2f}s")
            
            content = response.choices[0].message.content
            logger.info(f"  ✓ Ответ через LiteLLM: {content[:100]}...")
            logger.debug(f"  LiteLLM response: {response}")
            
            return True
        else:
            logger.error("  ✗ Некорректный ответ через LiteLLM")
            logger.debug(f"  LiteLLM response: {response}")
            return False
            
    except Exception as exc:
        logger.error(f"  ✗ Ошибка LiteLLM интеграции: {exc}")
        logger.debug("LiteLLM integration error details:", exc_info=True)
        return False


@click.command()
@click.option(
    '--timeout',
    type=int,
    default=30,
    help='Таймаут для тестирования в секундах [default: 30]'
)
@click.pass_context
def test(ctx, timeout):
    """Протестировать подключение к GigaChat."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 Timeout: {timeout}s")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    if not debug:
        click.echo("🧪 Тестирование подключения к GigaChat")
        click.echo("=" * 40)
    
    # Список тестов
    tests = [
        ("Переменные окружения", test_environment),
        ("TokenManager", test_token_manager),
        ("GigaChat API", test_gigachat_api),
        ("LiteLLM интеграция", test_litellm_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if not debug:
            click.echo(f"\n📋 {test_name}:")
        
        try:
            if test_func():
                passed += 1
                if not verbose and not debug:
                    click.echo(f"  ✓ Пройден")
            else:
                if not verbose and not debug:
                    click.echo(f"  ✗ Провален")
        except Exception as exc:
            logger.error(f"Ошибка теста '{test_name}': {exc}")
            if debug:
                logger.debug(f"Test error details:", exc_info=True)
            if not verbose and not debug:
                click.echo(f"  ✗ Ошибка: {exc}")
    
    # Результаты
    if not debug:
        click.echo("\n" + "=" * 40)
        click.echo(f"📊 Результаты тестирования:")
        click.echo(f"  Пройдено: {passed}/{total}")
        click.echo(f"  Провалено: {total - passed}/{total}")
    
    if passed == total:
        if not debug:
            click.echo("  🎉 Все тесты пройдены!")
        logger.info("Все тесты пройдены успешно")
        sys.exit(0)
    else:
        if not debug:
            click.echo("  ⚠️  Некоторые тесты провалены")
        logger.error(f"Провалено тестов: {total - passed}")
        sys.exit(1)
