#!/usr/bin/env python3
"""
Модуль для автоматической синхронизации моделей прокси-провайдера.

Периодически запрашивает список доступных моделей с кастомного API endpoint
и динамически обновляет конфигурацию LiteLLM Router без перезапуска сервера.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class ModelSyncManager:
    """
    Менеджер для автоматической синхронизации моделей с внутренним GigaChat API.
    
    Запускает фоновый daemon-поток, который периодически:
    1. Запрашивает список моделей с API
    2. Сравнивает с текущим списком
    3. Добавляет новые модели / удаляет отсутствующие
    """

    def __init__(
        self,
        api_base: str,
        auth_header_name: str,
        auth_header_value: str,
        sync_interval: int = 300,
        model_prefix: str = "gigachat-",
        model_suffix: str = "-internal",
        timeout: int = 60,
    ):
        """
        Инициализация менеджера синхронизации.

        Args:
            api_base: Базовый URL внутреннего GigaChat API
            auth_header_name: Название заголовка аутентификации
            auth_header_value: Значение заголовка аутентификации
            sync_interval: Интервал синхронизации в секундах (по умолчанию: 300)
            model_prefix: Префикс для имен моделей (по умолчанию: "gigachat-")
            model_suffix: Суффикс для имен моделей (по умолчанию: "-internal")
            timeout: Таймаут для HTTP запросов в секундах
        """
        self.api_base = api_base.rstrip("/")
        self.auth_header_name = auth_header_name
        self.auth_header_value = auth_header_value
        self.sync_interval = sync_interval
        self.model_prefix = model_prefix
        self.model_suffix = model_suffix
        self.timeout = timeout

        # Состояние
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._known_models: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

        # Callback для обновления LiteLLM Router
        self._on_models_updated: Optional[callable] = None

    def set_update_callback(self, callback: callable) -> None:
        """
        Установить callback для обновления моделей в LiteLLM Router.

        Args:
            callback: Функция, принимающая список моделей для обновления
        """
        self._on_models_updated = callback

    def fetch_models(self) -> Optional[List[Dict[str, Any]]]:
        """
        Запросить список моделей с внутреннего GigaChat API.

        Returns:
            Список моделей в формате OpenAI или None при ошибке
        """
        try:
            url = f"{self.api_base}/models"
            headers = {
                self.auth_header_name: self.auth_header_value,
                "Content-Type": "application/json",
            }

            logger.debug(f"Запрос списка моделей: {url}")
            response = requests.get(
                url,
                headers=headers,
                timeout=self.timeout,
                verify=False,  # SSL verification отключена как в основном коде
            )
            response.raise_for_status()

            data = response.json()
            models = data.get("data", [])

            logger.info(f"✓ Получено {len(models)} моделей с API")
            return models

        except requests.exceptions.RequestException as exc:
            logger.error(f"Ошибка запроса моделей: {exc}")
            return None
        except Exception as exc:
            logger.error(f"Неожиданная ошибка при получении моделей: {exc}")
            return None

    def _normalize_model_name(self, api_model_name: str) -> str:
        """
        Преобразовать имя модели из API в формат для LiteLLM.

        Примеры:
            GigaChat-2-Max -> gigachat-2-max-proxy
            llama-3.1-70b -> llama-3.1-70b-proxy
            mistral-large -> mistral-large-proxy

        Args:
            api_model_name: Имя модели из API

        Returns:
            Нормализованное имя модели
        """
        # Просто приводим к lowercase и добавляем суффикс
        # Префикс больше не используется
        normalized = f"{api_model_name.lower()}{self.model_suffix}"
        return normalized

    def sync_models(self) -> bool:
        """
        Синхронизировать модели с API.

        Запрашивает список моделей, сравнивает с известными и обновляет конфигурацию.

        Returns:
            True если синхронизация прошла успешно, False при ошибке
        """
        models = self.fetch_models()
        if models is None:
            logger.warning("Не удалось получить список моделей, используется последний известный")
            return False

        with self._lock:
            # Создаём словарь новых моделей
            new_models = {}
            for model in models:
                model_id = model.get("id", "")
                if not model_id:
                    continue

                # Нормализуем имя модели
                normalized_name = self._normalize_model_name(model_id)

                # Создаём конфигурацию модели для LiteLLM
                new_models[normalized_name] = {
                    "model_name": normalized_name,
                    "litellm_params": {
                        "model": f"openai/{model_id}",
                        "api_base": self.api_base,
                        "api_key": "none",
                        "timeout": self.timeout,
                    },
                    "original_id": model_id,
                }

            # Определяем изменения (для логирования)
            added = set(new_models.keys()) - set(self._known_models.keys())
            removed = set(self._known_models.keys()) - set(new_models.keys())

            # Обновляем известные модели
            self._known_models = new_models

            # ВСЕГДА вызываем callback для обновления LiteLLM Router
            # Это гарантирует, что модели будут доступны даже если роутер
            # не был инициализирован при первой синхронизации
            if self._on_models_updated:
                try:
                    self._on_models_updated(list(new_models.values()))
                    logger.info("✓ Модели успешно обновлены в LiteLLM Router")
                except Exception as exc:
                    logger.error(f"Ошибка обновления моделей в Router: {exc}")
                    return False

            # Логируем изменения
            if added or removed:
                logger.info(f"Обнаружены изменения в списке моделей:")
                if added:
                    logger.info(f"  + Добавлено: {', '.join(added)}")
                if removed:
                    logger.info(f"  - Удалено: {', '.join(removed)}")
            else:
                logger.debug("Изменений в списке моделей не обнаружено, но модели обновлены в роутере")

        return True

    def _sync_loop(self) -> None:
        """
        Основной цикл синхронизации (выполняется в фоновом потоке).
        """
        logger.info(f"🔄 Запущен фоновый поток синхронизации моделей (интервал: {self.sync_interval}s)")

        logger.info("⏳ Ожидание 30 секунд перед первой синхронизацией...")
        logger.info("✓ Запуск первой синхронизации моделей")
        
        # Первая синхронизация сразу при старте
        try:
            self.sync_models()
        except Exception as exc:
            logger.error(f"Ошибка при первой синхронизации: {exc}")

        # Периодическая синхронизация
        while self._running:
            try:
                time.sleep(self.sync_interval)
                if self._running:  # Проверяем снова после sleep
                    self.sync_models()
            except Exception as exc:
                logger.error(f"Ошибка в цикле синхронизации: {exc}")

        logger.info("🛑 Фоновый поток синхронизации моделей остановлен")

    def start(self) -> None:
        """
        Запустить фоновую синхронизацию моделей.
        """
        if self._running:
            logger.warning("Синхронизация моделей уже запущена")
            return

        self._running = True
        self._thread = threading.Thread(target=self._sync_loop, daemon=True)
        self._thread.start()
        logger.info("✓ Фоновая синхронизация моделей запущена")

    def stop(self) -> None:
        """
        Остановить фоновую синхронизацию моделей.
        """
        if not self._running:
            return

        logger.info("Остановка синхронизации моделей...")
        self._running = False

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5)

        logger.info("✓ Синхронизация моделей остановлена")

    def get_known_models(self) -> List[Dict[str, Any]]:
        """
        Получить список известных моделей.

        Returns:
            Список конфигураций моделей
        """
        with self._lock:
            return list(self._known_models.values())


# Глобальный экземпляр менеджера
_global_model_sync_manager: Optional[ModelSyncManager] = None


def get_global_model_sync_manager() -> Optional[ModelSyncManager]:
    """
    Получить глобальный экземпляр ModelSyncManager.

    Returns:
        Глобальный экземпляр или None если не инициализирован
    """
    return _global_model_sync_manager


def init_global_model_sync_manager(
    api_base: str,
    auth_header_name: str,
    auth_header_value: str,
    sync_interval: int = 300,
    model_prefix: str = "gigachat-",
    model_suffix: str = "-internal",
    timeout: int = 60,
) -> ModelSyncManager:
    """
    Инициализировать глобальный экземпляр ModelSyncManager.

    Args:
        api_base: Базовый URL внутреннего GigaChat API
        auth_header_name: Название заголовка аутентификации
        auth_header_value: Значение заголовка аутентификации
        sync_interval: Интервал синхронизации в секундах
        model_prefix: Префикс для имен моделей
        model_suffix: Суффикс для имен моделей
        timeout: Таймаут для HTTP запросов

    Returns:
        Инициализированный экземпляр ModelSyncManager
    """
    global _global_model_sync_manager

    _global_model_sync_manager = ModelSyncManager(
        api_base=api_base,
        auth_header_name=auth_header_name,
        auth_header_value=auth_header_value,
        sync_interval=sync_interval,
        model_prefix=model_prefix,
        model_suffix=model_suffix,
        timeout=timeout,
    )

    return _global_model_sync_manager
