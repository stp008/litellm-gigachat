#!/usr/bin/env python3
"""
Callback для интеграции синхронизации моделей с LiteLLM Router.

Этот модуль предоставляет функции для динамического обновления списка моделей
в LiteLLM Router на основе данных, полученных от ModelSyncManager.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Глобальная ссылка на LiteLLM proxy app (будет установлена при инициализации)
_litellm_proxy_app = None


def set_litellm_proxy_app(app: Any) -> None:
    """
    Установить ссылку на LiteLLM proxy app для обновления моделей.

    Args:
        app: Экземпляр LiteLLM proxy app
    """
    global _litellm_proxy_app
    _litellm_proxy_app = app
    logger.debug("LiteLLM proxy app установлен для синхронизации моделей")


def update_models_in_router(models: List[Dict[str, Any]]) -> None:
    """
    Обновить список моделей в LiteLLM Router.

    Эта функция вызывается ModelSyncManager при обнаружении изменений в списке моделей.

    Args:
        models: Список конфигураций моделей для добавления/обновления
    """
    try:
        # Импортируем litellm здесь, чтобы избежать циклических зависимостей
        import litellm
        from litellm.proxy.proxy_server import llm_router, llm_model_list, user_config_file_path
        
        logger.info(f"Обновление {len(models)} моделей в LiteLLM Router...")

        # Получаем текущий список моделей
        current_model_names = set()
        if llm_model_list:
            current_model_names = {m.get("model_name") for m in llm_model_list if m.get("model_name")}

        # Определяем модели для добавления
        new_model_names = {m.get("model_name") for m in models if m.get("model_name")}
        
        # Фильтруем только internal модели для синхронизации
        internal_models = [m for m in models if m.get("model_name", "").endswith("-internal")]
        
        if not internal_models:
            logger.debug("Нет internal моделей для синхронизации")
            return

        # Добавляем/обновляем модели в глобальный список
        for model_config in internal_models:
            model_name = model_config.get("model_name")
            
            # Проверяем, есть ли уже такая модель
            existing_model = None
            if llm_model_list:
                for idx, existing in enumerate(llm_model_list):
                    if existing.get("model_name") == model_name:
                        existing_model = idx
                        break
            
            if existing_model is not None:
                # Обновляем существующую модель
                llm_model_list[existing_model] = model_config
                logger.debug(f"Обновлена модель: {model_name}")
            else:
                # Добавляем новую модель
                if llm_model_list is not None:
                    llm_model_list.append(model_config)
                logger.info(f"Добавлена новая модель: {model_name}")

        # Пересоздаём router с обновлённым списком моделей
        if llm_router and llm_model_list:
            try:
                # Обновляем deployments в существующем router
                llm_router.set_model_list(llm_model_list)
                logger.info("✓ LiteLLM Router успешно обновлён")
            except Exception as router_exc:
                logger.warning(f"Не удалось обновить router напрямую: {router_exc}")
                # Альтернативный подход - логируем для информации
                logger.info("Модели будут доступны при следующем запросе")

    except ImportError as imp_exc:
        logger.error(f"Ошибка импорта LiteLLM модулей: {imp_exc}")
    except Exception as exc:
        logger.error(f"Ошибка обновления моделей в Router: {exc}", exc_info=True)


def get_update_callback() -> callable:
    """
    Получить callback функцию для обновления моделей.

    Returns:
        Функция callback для передачи в ModelSyncManager
    """
    return update_models_in_router
