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

def check_environment() -> bool:
    """Проверка обязательных переменных окружения."""
    if "GIGACHAT_AUTH_KEY" not in os.environ:
        logger.error(
            "Переменная окружения GIGACHAT_AUTH_KEY не установлена!\n"
            "export GIGACHAT_AUTH_KEY='ваш_authorization_key'",
        )
        return False

    logger.info("✓ GIGACHAT_AUTH_KEY найден")
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
    """Проверка доступности модулей GigaChat интеграции."""
    try:
        # Просто проверяем, что модули доступны
        # Callback будет загружен автоматически через config.yml
        from ..callbacks.token_callback import get_gigachat_callback
        from ..core.token_manager import get_global_token_manager
        
        # Проверяем, что token manager работает
        token_manager = get_global_token_manager()
        logger.info("✓ Модули GigaChat интеграции доступны")
        logger.info("✓ Token manager инициализирован")
        return True
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("Ошибка проверки интеграции: %s", exc)
        return False


# ─────────────────────────────────────────────  Запуск прокси ─────────────────────────────────────────────

def start_proxy_server(
    host: str = "0.0.0.0",
    port: int = 4000,
    config_file: str = "config.yml",
    verbose: bool = False,
    debug: bool = False,
) -> bool:
    """Запускает LiteLLM Proxy, возвращает True при успешном старте."""

    if not Path(config_file).exists():
        logger.error("Конфигурационный файл %s не найден!", config_file)
        return False

    if verbose or debug:
        logger.info("Запуск LiteLLM прокси‑сервера…")
        logger.info("  Host: %s", host)
        logger.info("  Port: %s", port)
        logger.info("  Config: %s", config_file)
        if debug:
            logger.info("  Debug mode: enabled")
        if verbose:
            logger.info("  Verbose mode: enabled")

    # Ключевое исправление — вызываем CLI‑скрипт `litellm`
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
    """Запускает все проверки и прокси‑сервер."""
    
    # Парсинг аргументов командной строки
    parser = argparse.ArgumentParser(
        description="LiteLLM прокси-сервер для GigaChat API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  litellm-gigachat                                    # Запуск с настройками по умолчанию
  litellm-gigachat --host 127.0.0.1 --port 8000      # Кастомный хост и порт
  litellm-gigachat --config my_config.yml             # Кастомный файл конфигурации
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
        "--version",
        action="version",
        version="litellm-gigachat 0.1.3"
    )
    
    args = parser.parse_args()

    # Загружаем переменные окружения из .env файла
    load_dotenv()

    logger.info("🚀 Запуск LiteLLM прокси‑сервера для GigaChat")
    logger.info("=" * 50)

    if not (check_environment() and check_dependencies() and setup_certificates() and setup_gigachat_integration()):
        sys.exit(1)

    logger.info("Все проверки пройдены, запуск сервера…")
    logger.info("=" * 50)

    if start_proxy_server(host=args.host, port=args.port, config_file=args.config):
        logger.info("Сервер завершил работу")
    else:
        logger.error("Ошибка при работе сервера")
        sys.exit(1)


if __name__ == "__main__":
    main()
