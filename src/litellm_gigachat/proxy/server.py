#!/usr/bin/env python3
"""
Скрипт для запуска LiteLLM прокси‑сервера с поддержкой автоматического
обновления токенов GigaChat.

💡 Актуальные изменения (июль 2025)
-----------------------------------
* Пакет `litellm` больше **не содержит** `__main__.py`, поэтому `python -m litellm` и
  `python -m litellm.proxy` бросают ошибку.
* Вместо этого используется **CLI‑скрипт** `litellm`, который ставится вместе с
  `litellm[proxy]` и умеет поднимать сервер.
* Обновлена сборка команды запуска и мелкие улучшения типизации.
"""

from __future__ import annotations

import argparse
import logging
import os
import subprocess
import sys
from importlib import metadata
from pathlib import Path
import certifi
from dotenv import load_dotenv

# ─────────────────────────────────────────  Настройка логов ─────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ────────────────────────────────────────  Вспомогательные функции ────────────────────────────────────────

def has_official_gigachat_models(config_file: str) -> bool:
    """
    Проверяет наличие официальных моделей GigaChat в конфигурации.
    
    Официальные модели - это модели с api_base содержащим 'gigachat.devices.sberbank.ru'
    
    Args:
        config_file: Путь к файлу конфигурации
        
    Returns:
        True если есть официальные модели GigaChat, False иначе
    """
    try:
        import yaml
        
        if not Path(config_file).exists():
            logger.warning(f"Файл конфигурации {config_file} не найден")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not config or 'model_list' not in config:
            logger.warning("Конфигурация не содержит model_list")
            return False
        
        # Проверяем каждую модель
        for model in config['model_list']:
            if not isinstance(model, dict):
                continue
            
            litellm_params = model.get('litellm_params', {})
            api_base = litellm_params.get('api_base', '')
            
            # Проверяем, является ли это официальной моделью GigaChat
            if 'gigachat.devices.sberbank.ru' in api_base.lower():
                logger.debug(f"Найдена официальная модель GigaChat: {model.get('model_name', 'unknown')}")
                return True
        
        logger.debug("Официальные модели GigaChat не найдены в конфигурации")
        return False
        
    except Exception as exc:
        logger.error(f"Ошибка при проверке конфигурации: {exc}")
        # В случае ошибки считаем, что модели есть (безопасный вариант)
        return True


def check_environment(config_file: str) -> bool:
    """
    Проверка обязательных переменных окружения.
    
    GIGACHAT_AUTH_KEY обязателен только если в конфигурации есть официальные модели GigaChat.
    
    Args:
        config_file: Путь к файлу конфигурации
        
    Returns:
        True если все необходимые переменные установлены, False иначе
    """
    # Проверяем, есть ли официальные модели GigaChat в конфигурации
    has_official_models = has_official_gigachat_models(config_file)
    
    if has_official_models:
        # Если есть официальные модели, GIGACHAT_AUTH_KEY обязателен
        if "GIGACHAT_AUTH_KEY" not in os.environ:
            logger.error(
                "❌ Переменная окружения GIGACHAT_AUTH_KEY не установлена!\n"
                "   В конфигурации найдены официальные модели GigaChat, требующие аутентификацию.\n"
                "   export GIGACHAT_AUTH_KEY='ваш_authorization_key'",
            )
            return False
        logger.info("✓ GIGACHAT_AUTH_KEY найден")
    else:
        # Если нет официальных моделей, GIGACHAT_AUTH_KEY не обязателен
        if "GIGACHAT_AUTH_KEY" in os.environ:
            logger.info("✓ GIGACHAT_AUTH_KEY найден")
        else:
            logger.info("ℹ️  GIGACHAT_AUTH_KEY не установлен (не требуется для прокси-моделей)")
    
    return True


def check_dependencies() -> bool:
    """Проверка установленных зависимостей."""
    try:
        import litellm  # noqa: F401 — проверка импорта
        logger.info("✓ LiteLLM версия: %s", metadata.version("litellm"))
    except ImportError:
        logger.error("LiteLLM не установлен. Установите: pip install 'litellm[proxy]'")
        return False

    try:
        import requests  # noqa: F401
        logger.info("✓ Requests установлен")
    except ImportError:
        logger.error("Requests не установлен. Установите: pip install requests")
        return False

    return True


def setup_certificates() -> bool:
    """Настройка российских доверенных корневых сертификатов."""
    try:
        # Получаем путь к файлу сертификатов certifi
        cert_file = certifi.where()
        logger.info("Файл сертификатов certifi: %s", cert_file)
        
        # URL российского доверенного корневого сертификата
        cert_url = "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt"
        
        # Проверяем, не добавлен ли уже сертификат
        try:
            with open(cert_file, 'r', encoding='utf-8') as f:
                cert_content = f.read()
                if "Russian Trusted Root CA" in cert_content or "gu-st.ru" in cert_content:
                    logger.info("✓ Российский корневой сертификат уже установлен")
                    return True
        except Exception as read_exc:
            logger.warning("Не удалось прочитать файл сертификатов: %s", read_exc)
        
        # Загружаем и добавляем сертификат
        logger.info("Загрузка российского корневого сертификата...")
        
        cmd = [
            "curl", "-k", cert_url, "-w", "\\n"
        ]
        
        try:
            # Выполняем curl и получаем содержимое сертификата
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
            cert_data = result.stdout.strip()
            
            if not cert_data or "BEGIN CERTIFICATE" not in cert_data:
                logger.error("Получены некорректные данные сертификата")
                return False
            
            # Добавляем сертификат в файл certifi
            with open(cert_file, 'a', encoding='utf-8') as f:
                f.write('\n')
                f.write('# Russian Trusted Root CA (added by litellm-gigachat)\n')
                f.write(cert_data)
                f.write('\n')
            
            logger.info("✓ Российский корневой сертификат успешно добавлен")
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("Таймаут при загрузке сертификата")
            return False
        except subprocess.CalledProcessError as proc_exc:
            logger.error("Ошибка выполнения curl: %s", proc_exc)
            return False
        except PermissionError:
            logger.error("Нет прав на запись в файл сертификатов: %s", cert_file)
            return False
        except Exception as write_exc:
            logger.error("Ошибка записи сертификата: %s", write_exc)
            return False
            
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Ошибка настройки сертификатов: %s", exc)
        return False


def setup_gigachat_integration() -> bool:
    """
    Проверка доступности модулей GigaChat интеграции.
    
    Если GIGACHAT_AUTH_KEY не установлен, token manager не будет инициализирован,
    но это не критично для работы с прокси-моделями.
    """
    try:
        # Проверяем, что модули доступны
        from ..callbacks.token_callback import get_gigachat_callback
        from ..core.token_manager import get_global_token_manager
        
        logger.info("✓ Модули GigaChat интеграции доступны")
        
        # Пытаемся инициализировать token manager только если есть GIGACHAT_AUTH_KEY
        if "GIGACHAT_AUTH_KEY" in os.environ:
            try:
                token_manager = get_global_token_manager()
                logger.info("✓ Token manager инициализирован")
            except Exception as token_exc:
                logger.warning(f"⚠️  Не удалось инициализировать token manager: {token_exc}")
                logger.warning("   Официальные модели GigaChat могут не работать")
        else:
            logger.debug("Token manager не инициализирован (GIGACHAT_AUTH_KEY не установлен)")
        
        return True
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Ошибка проверки интеграции: %s", exc)
        return False


def setup_model_sync() -> bool:
    """
    Настройка автоматической синхронизации моделей для прокси-провайдера.
    
    Returns:
        True если синхронизация настроена успешно, False если отключена или произошла ошибка
    """
    try:
        # Проверяем, включена ли синхронизация моделей
        model_sync_enabled = os.environ.get("MODEL_SYNC_ENABLED", "false").lower() == "true"
        proxy_enabled = os.environ.get("PROXY_PROVIDER_ENABLED", "false").lower() == "true"
        
        if not model_sync_enabled:
            logger.info("ℹ️  Автоматическая синхронизация моделей отключена (MODEL_SYNC_ENABLED=false)")
            return True
        
        if not proxy_enabled:
            logger.warning("⚠️  MODEL_SYNC_ENABLED=true, но PROXY_PROVIDER_ENABLED=false")
            logger.warning("   Синхронизация моделей работает только с прокси-провайдером")
            return True
        
        # Получаем параметры из переменных окружения
        api_base = os.environ.get("PROXY_PROVIDER_URL")
        auth_header_name = os.environ.get("PROXY_PROVIDER_AUTH_HEADER", "X-Client-Id")
        auth_header_value = os.environ.get("PROXY_PROVIDER_AUTH_VALUE")
        
        if not api_base or not auth_header_value:
            logger.error("❌ Для синхронизации моделей требуются PROXY_PROVIDER_URL и PROXY_PROVIDER_AUTH_VALUE")
            return False
        
        # Получаем дополнительные параметры
        sync_interval = int(os.environ.get("MODEL_SYNC_INTERVAL", "300"))
        model_suffix = os.environ.get("PROXY_PROVIDER_MODEL_SUFFIX", "proxy")
        timeout = int(os.environ.get("GIGACHAT_TIMEOUT", "60"))
        
        # Импортируем модули синхронизации
        from ..core.model_sync import init_global_model_sync_manager
        from ..callbacks.model_sync_callback import get_update_callback
        
        # Инициализируем менеджер синхронизации
        # Префикс больше не используется, передаём пустую строку
        sync_manager = init_global_model_sync_manager(
            api_base=api_base,
            auth_header_name=auth_header_name,
            auth_header_value=auth_header_value,
            sync_interval=sync_interval,
            model_prefix="",  # Префикс не используется
            model_suffix=f"-{model_suffix}",
            timeout=timeout,
        )
        
        # Устанавливаем callback для обновления моделей
        sync_manager.set_update_callback(get_update_callback())
        
        # Запускаем фоновую синхронизацию
        sync_manager.start()
        
        logger.info("✓ Автоматическая синхронизация моделей запущена")
        logger.info(f"  Интервал: {sync_interval} секунд")
        logger.info(f"  API: {api_base}")
        logger.info(f"  Суффикс моделей: -{model_suffix}")
        
        return True
        
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(f"Ошибка настройки синхронизации моделей: {exc}")
        return False


# ─────────────────────────────────────────────  Запуск прокси ─────────────────────────────────────────────

def start_proxy_server(
    host: str = "0.0.0.0",
    port: int = 4000,
    config_file: str = "config.yml",
    verbose: bool = False,
    debug: bool = False,
) -> bool:
    """Выполняет все проверки и запускает LiteLLM Proxy."""

    logger.info("🚀 Запуск LiteLLM прокси‑сервера для GigaChat")
    logger.info("=" * 50)

    # 1. Предварительные проверки
    if not (check_environment(config_file) and check_dependencies() and setup_certificates() and setup_gigachat_integration()):
        logger.error("Предварительные проверки не пройдены. Запуск отменен.")
        return False

    # 2. Настройка синхронизации моделей (если включена)
    if not setup_model_sync():
        logger.error("Ошибка настройки синхронизации моделей. Запуск отменен.")
        return False

    logger.info("✓ Все проверки пройдены, запуск сервера…")
    logger.info("=" * 50)

    # 2. Проверка файла конфигурации
    if not Path(config_file).exists():
        logger.error("Конфигурационный файл %s не найден!", config_file)
        return False

    # 3. Логирование параметров запуска
    if verbose or debug:
        logger.info("Запуск LiteLLM прокси‑сервера…")
        logger.info("  Host: %s", host)
        logger.info("  Port: %s", port)
        logger.info("  Config: %s", config_file)
        if debug:
            logger.info("  Debug mode: enabled")
        if verbose:
            logger.info("  Verbose mode: enabled")

    # 4. Сборка команды запуска
    cmd: list[str] = [
        "litellm",  # console‑script, попадающий в venv/bin
        "--config",
        config_file,
        "--host",
        host,
        "--port",
        str(port),
    ]
    
    # Добавляем debug флаги если нужно
    if debug:
        cmd.append("--detailed_debug")
    elif verbose:
        cmd.append("--debug")

    if verbose or debug:
        logger.info("Выполнение команды: %s", " ".join(cmd))

    # 5. Запуск процесса
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as exc:
        logger.error("Ошибка запуска прокси‑сервера: %s", exc)
        return False
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершаем работу…")
        return True


# ────────────────────────────────────────────  Точка входа ────────────────────────────────────────────

def main() -> None:  # noqa: D401 — imperative
    """Парсит аргументы и запускает прокси-сервер."""
    
    # Загружаем переменные окружения из .env файла
    load_dotenv()

    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description="LiteLLM прокси-сервер для GigaChat API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  litellm-gigachat                                    # Запуск с настройками по умолчанию
  litellm-gigachat --host 127.0.0.1 --port 8000      # Кастомный хост и порт
  litellm-gigachat --config my_config.yml             # Кастомный файл конфигурации
  litellm-gigachat --verbose                          # Включить подробный вывод
  litellm-gigachat --debug                            # Включить режим отладки
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Хост для прокси-сервера (по умолчанию: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=4000,
        help="Порт для прокси-сервера (по умолчанию: 4000)"
    )
    
    parser.add_argument(
        "--config",
        default="../config.yml",
        help="Путь к файлу конфигурации (по умолчанию: config.yml)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Включить подробный вывод (эквивалент --debug для litellm)"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Включить режим отладки (эквивалент --detailed_debug для litellm)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version="litellm-gigachat 0.1.4"
    )
    
    args = parser.parse_args()

    if start_proxy_server(
        host=args.host,
        port=args.port,
        config_file=args.config,
        verbose=args.verbose,
        debug=args.debug
    ):
        logger.info("Сервер завершил работу")
    else:
        logger.error("Ошибка при работе сервера")
        sys.exit(1)


if __name__ == "__main__":
    main()
