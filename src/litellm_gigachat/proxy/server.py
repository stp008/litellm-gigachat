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

import logging
import os
import subprocess
from importlib import metadata
from pathlib import Path
import certifi

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
    """
    Настройка российских доверенных корневых сертификатов.
    
    Установка сертификатов опциональна и контролируется переменной окружения INSTALL_RUSSIAN_CERTS.
    По умолчанию отключена для совместимости с внутренними стендами без интернета.
    
    Returns:
        True всегда (ошибки установки сертификатов не критичны)
    """
    # Проверяем, нужно ли устанавливать сертификаты
    install_certs = os.environ.get("INSTALL_RUSSIAN_CERTS", "false").lower() == "true"
    
    if not install_certs:
        logger.info("ℹ️  Установка российских сертификатов отключена (INSTALL_RUSSIAN_CERTS=false)")
        logger.info("   Для публичного GigaChat API установите INSTALL_RUSSIAN_CERTS=true")
        return True
    
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
                logger.warning("⚠️  Получены некорректные данные сертификата")
                logger.warning("   Продолжаем без установки сертификата")
                return True
            
            # Добавляем сертификат в файл certifi
            with open(cert_file, 'a', encoding='utf-8') as f:
                f.write('\n')
                f.write('# Russian Trusted Root CA (added by litellm-gigachat)\n')
                f.write(cert_data)
                f.write('\n')
            
            logger.info("✓ Российский корневой сертификат успешно добавлен")
            return True
            
        except subprocess.TimeoutExpired:
            logger.warning("⚠️  Таймаут при загрузке сертификата")
            logger.warning("   Продолжаем без установки сертификата")
            return True
        except subprocess.CalledProcessError as proc_exc:
            logger.warning(f"⚠️  Ошибка выполнения curl: {proc_exc}")
            logger.warning("   Продолжаем без установки сертификата")
            return True
        except PermissionError:
            logger.warning(f"⚠️  Нет прав на запись в файл сертификатов: {cert_file}")
            logger.warning("   Продолжаем без установки сертификата")
            return True
        except Exception as write_exc:
            logger.warning(f"⚠️  Ошибка записи сертификата: {write_exc}")
            logger.warning("   Продолжаем без установки сертификата")
            return True
            
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning(f"⚠️  Ошибка настройки сертификатов: {exc}")
        logger.warning("   Продолжаем без установки сертификата")
        return True


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


def setup_model_sync(config_file: str = "config.yml") -> bool:
    """
    Настройка автоматической синхронизации моделей для прокси-провайдеров.
    
    Args:
        config_file: Путь к файлу конфигурации
    
    Returns:
        True если синхронизация настроена успешно, False если отключена или произошла ошибка
    """
    try:
        logger.info("🔍 Начало настройки синхронизации моделей...")
        
        # Импортируем необходимые модули
        from ..core.proxy_provider_manager import init_multi_proxy_provider_manager
        from ..core.multi_model_sync import init_global_multi_model_sync_manager
        from ..callbacks.model_sync_callback import get_update_callback
        
        # Инициализируем менеджер прокси-провайдеров
        provider_manager = init_multi_proxy_provider_manager(config_file)
        
        # Получаем список всех провайдеров
        providers = provider_manager.get_all_providers()
        
        if not providers:
            logger.info("ℹ️  Нет настроенных прокси-провайдеров")
            return True
        
        # Фильтруем провайдеров с включенной синхронизацией
        sync_providers = [p for p in providers if p.sync_enabled]
        
        if not sync_providers:
            logger.info("ℹ️  Автоматическая синхронизация моделей отключена для всех провайдеров")
            return True
        
        logger.info(f"Найдено {len(sync_providers)} провайдеров с включенной синхронизацией")
        
        # Инициализируем multi sync manager
        multi_sync_manager = init_global_multi_model_sync_manager()
        
        # Устанавливаем callback для обновления моделей
        multi_sync_manager.set_update_callback(get_update_callback())
        
        # Добавляем каждого провайдера
        added_count = 0
        for provider in sync_providers:
            if multi_sync_manager.add_provider(provider):
                added_count += 1
                logger.info(f"  ✓ {provider.name}: интервал {provider.sync_interval}s, суффикс -{provider.suffix}")
        
        if added_count == 0:
            logger.warning("⚠️  Не удалось добавить ни одного провайдера для синхронизации")
            return False
        
        # Запускаем фоновую синхронизацию для всех провайдеров
        multi_sync_manager.start_all()
        
        logger.info(f"✓ Автоматическая синхронизация моделей запущена для {added_count} провайдеров")
        
        return True
        
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(f"Ошибка настройки синхронизации моделей: {exc}")
        logger.exception("Детали ошибки:")
        return False


# ─────────────────────────────────────────────  Запуск прокси ─────────────────────────────────────────────

def start_proxy_server(
    host: str = "0.0.0.0",
    port: int = 4000,
    config_file: str = "config.yml",
    verbose: bool = False,
    debug: bool = False,
) -> bool:
    """Запускает LiteLLM Proxy сервер (проверки должны быть выполнены до вызова)."""

    # Проверка файла конфигурации
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

    # 4. Запуск через uvicorn программно (в том же процессе)
    try:
        import uvicorn
        import asyncio
        from litellm.proxy.proxy_server import app, initialize
        
        # Инициализация LiteLLM с конфигом
        async def init_and_start():
            # Инициализируем LiteLLM
            await initialize(
                config=config_file,
                debug=debug,
                detailed_debug=debug
            )
            
            # Теперь llm_router существует - запускаем синхронизацию моделей
            if not setup_model_sync(config_file):
                logger.warning("⚠️ Синхронизация моделей не запущена")
        
        # Запускаем инициализацию
        asyncio.run(init_and_start())
        
        # Настройка uvicorn
        log_level = "debug" if debug else ("info" if verbose else "info")
        
        logger.info(f"🚀 Запуск uvicorn на {host}:{port}")
        
        # Запуск uvicorn
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level=log_level,
            access_log=verbose or debug
        )
        
        return True
        
    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания, завершаем работу…")
        return True
    except Exception as exc:
        logger.error("Ошибка запуска прокси‑сервера: %s", exc)
        logger.exception("Детали ошибки:")
        return False
