#!/usr/bin/env python3
"""
Модуль для управления несколькими менеджерами синхронизации моделей.

Позволяет синхронизировать модели с нескольких прокси-провайдеров одновременно.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Optional, Any

from .model_sync import ModelSyncManager
from .proxy_provider_manager import ProxyProviderConfig

logger = logging.getLogger(__name__)


class MultiModelSyncManager:
    """
    Менеджер для управления синхронизацией моделей с нескольких прокси-провайдеров.
    
    Создаёт отдельный ModelSyncManager для каждого провайдера с включенной синхронизацией.
    """

    def __init__(self):
        """Инициализация менеджера"""
        self._sync_managers: Dict[str, ModelSyncManager] = {}
        self._on_models_updated: Optional[callable] = None

    def add_provider(self, provider: ProxyProviderConfig) -> bool:
        """
        Добавить провайдера для синхронизации моделей.

        Args:
            provider: Конфигурация прокси-провайдера

        Returns:
            True если провайдер добавлен успешно
        """
        if not provider.sync_enabled:
            logger.debug(f"Синхронизация отключена для провайдера {provider.name}")
            return False

        if provider.name in self._sync_managers:
            logger.warning(f"Провайдер {provider.name} уже добавлен")
            return False

        try:
            # Создаём ModelSyncManager для этого провайдера
            sync_manager = ModelSyncManager(
                api_base=provider.url,
                auth_header_name=provider.auth_header,
                auth_header_value=provider.auth_value,
                sync_interval=provider.sync_interval,
                model_suffix=f"-{provider.suffix}",
                timeout=provider.timeout,
                provider_name=provider.name
            )

            # Устанавливаем callback для обновления моделей
            if self._on_models_updated:
                sync_manager.set_update_callback(self._on_models_updated)

            self._sync_managers[provider.name] = sync_manager
            return True

        except Exception as exc:
            logger.error(f"Ошибка добавления провайдера {provider.name}: {exc}")
            return False

    def set_update_callback(self, callback: callable) -> None:
        """
        Установить callback для обновления моделей в LiteLLM Router.

        Args:
            callback: Функция, принимающая список моделей для обновления
        """
        self._on_models_updated = callback

        # Обновляем callback для всех существующих sync managers
        for sync_manager in self._sync_managers.values():
            sync_manager.set_update_callback(callback)

    def start_all(self) -> None:
        """Запустить синхронизацию для всех провайдеров"""
        if not self._sync_managers:
            logger.info("Нет провайдеров для синхронизации")
            return

        logger.info(f"Запуск синхронизации для {len(self._sync_managers)} провайдеров")

        for provider_name, sync_manager in self._sync_managers.items():
            try:
                sync_manager.start()
                logger.info(f"Синхронизация запущена для провайдера {provider_name}")
            except Exception as exc:
                logger.error(f"Ошибка запуска синхронизации для {provider_name}: {exc}")

    def stop_all(self) -> None:
        """Остановить синхронизацию для всех провайдеров"""
        if not self._sync_managers:
            return

        logger.info(f"Остановка синхронизации для {len(self._sync_managers)} провайдеров...")

        for provider_name, sync_manager in self._sync_managers.items():
            try:
                sync_manager.stop()
                logger.info(f"Синхронизация остановлена для провайдера {provider_name}")
            except Exception as exc:
                logger.error(f"Ошибка остановки синхронизации для {provider_name}: {exc}")

    def get_all_models(self) -> List[Dict[str, Any]]:
        """
        Получить все синхронизированные модели со всех провайдеров.

        Returns:
            Список конфигураций моделей
        """
        all_models = []

        for provider_name, sync_manager in self._sync_managers.items():
            try:
                models = sync_manager.get_known_models()
                all_models.extend(models)
                logger.debug(f"Получено {len(models)} моделей от провайдера {provider_name}")
            except Exception as exc:
                logger.error(f"Ошибка получения моделей от {provider_name}: {exc}")

        return all_models

    def get_provider_models(self, provider_name: str) -> List[Dict[str, Any]]:
        """
        Получить модели конкретного провайдера.

        Args:
            provider_name: Имя провайдера

        Returns:
            Список конфигураций моделей или пустой список
        """
        sync_manager = self._sync_managers.get(provider_name)
        if not sync_manager:
            logger.warning(f"Провайдер {provider_name} не найден")
            return []

        return sync_manager.get_known_models()

    def sync_all(self) -> bool:
        """
        Выполнить синхронизацию для всех провайдеров.

        Returns:
            True если хотя бы одна синхронизация прошла успешно
        """
        if not self._sync_managers:
            logger.warning("Нет провайдеров для синхронизации")
            return False

        success_count = 0
        for provider_name, sync_manager in self._sync_managers.items():
            try:
                if sync_manager.sync_models():
                    success_count += 1
                    logger.debug(f"Синхронизация успешна для {provider_name}")
                else:
                    logger.warning(f"Синхронизация не удалась для {provider_name}")
            except Exception as exc:
                logger.error(f"Ошибка синхронизации для {provider_name}: {exc}")

        logger.info(f"Синхронизация завершена: {success_count}/{len(self._sync_managers)} успешно")
        return success_count > 0

    def get_status(self) -> Dict[str, Any]:
        """
        Получить статус синхронизации для всех провайдеров.

        Returns:
            Словарь со статусом каждого провайдера
        """
        status = {
            "total_providers": len(self._sync_managers),
            "providers": {}
        }

        for provider_name, sync_manager in self._sync_managers.items():
            models = sync_manager.get_known_models()
            status["providers"][provider_name] = {
                "running": sync_manager._running,
                "models_count": len(models),
                "models": [m.get("model_name", "unknown") for m in models]
            }

        return status


# Глобальный экземпляр менеджера
_global_multi_model_sync_manager: Optional[MultiModelSyncManager] = None


def get_global_multi_model_sync_manager() -> Optional[MultiModelSyncManager]:
    """
    Получить глобальный экземпляр MultiModelSyncManager.

    Returns:
        Глобальный экземпляр или None если не инициализирован
    """
    return _global_multi_model_sync_manager


def init_global_multi_model_sync_manager() -> MultiModelSyncManager:
    """
    Инициализировать глобальный экземпляр MultiModelSyncManager.

    Returns:
        Инициализированный экземпляр MultiModelSyncManager
    """
    global _global_multi_model_sync_manager

    _global_multi_model_sync_manager = MultiModelSyncManager()

    return _global_multi_model_sync_manager
