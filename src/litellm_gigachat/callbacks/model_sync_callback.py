#!/usr/bin/env python3
"""
Callback для интеграции синхронизации моделей с LiteLLM Router.
"""

from __future__ import annotations

import hashlib
import logging
import threading
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

# Глобальная блокировка для предотвращения одновременного обновления
_update_lock = threading.Lock()


def update_models_in_router(models: List[Dict[str, Any]], provider_name: str = "unknown", model_suffix: str = None) -> None:
    """
    Обновить список моделей в LiteLLM Router через upsert_deployment.
    
    Теперь работает в том же процессе, что и LiteLLM сервер,
    поэтому изменения сразу видны в /v1/models.
    
    Использует блокировку для предотвращения race conditions.
    
    Args:
        models: Список моделей для обновления
        provider_name: Имя провайдера (для логирования)
        model_suffix: Суффикс моделей провайдера (например, "-p1", "-p2")
    """
    # Используем блокировку для предотвращения одновременного выполнения
    with _update_lock:
        try:
            import litellm.proxy.proxy_server as proxy_server
            from litellm.types.router import Deployment, LiteLLM_Params, ModelInfo
            import os
            
            logger.info(f"Запущен процесс обновления {len(models)} моделей в LiteLLM (провайдер: {provider_name})...")

            # Проверяем, что Router существует
            if not hasattr(proxy_server, "llm_router") or proxy_server.llm_router is None:
                logger.warning("Router ещё не инициализирован, пропускаем обновление")
                return
            
            # 1. Удаляем ВСЕ старые deployments с суффиксом этого провайдера
            # Это предотвращает дубликаты и устаревшие модели
            deleted_count = 0
            if model_suffix and hasattr(proxy_server.llm_router, 'model_list'):
                original_count = len(proxy_server.llm_router.model_list)
                
                # Фильтруем - оставляем только модели БЕЗ суффикса этого провайдера
                proxy_server.llm_router.model_list = [
                    d for d in proxy_server.llm_router.model_list 
                    if not d.get("model_name", "").endswith(model_suffix)
                ]
                
                deleted_count = original_count - len(proxy_server.llm_router.model_list)
                if deleted_count > 0:
                    logger.info(f"Удалено {deleted_count} старых deployments провайдера {provider_name} с суффиксом {model_suffix}")
            
            # 2. Добавляем/обновляем модели из API
            logger.info(f"Обновление {len(models)} моделей в Router...")
            
            added_count = 0
            updated_count = 0
            
            for model in models:
                try:
                    model_name = model.get("model_name")
                    litellm_params_dict = model.get("litellm_params", {})
                    
                    if not model_name or not litellm_params_dict:
                        logger.warning(f"Пропуск модели с неполными данными: {model}")
                        continue
                    
                    # Удаляем существующую модель с таким же именем (если есть)
                    # Это предотвращает дубликаты при использовании upsert_deployment
                    existing_count = len(proxy_server.llm_router.model_list)
                    proxy_server.llm_router.model_list = [
                        d for d in proxy_server.llm_router.model_list 
                        if d.get("model_name") != model_name
                    ]
                    was_existing = len(proxy_server.llm_router.model_list) < existing_count
                    
                    # Создаём LiteLLM_Params
                    litellm_params = LiteLLM_Params(
                        model=litellm_params_dict.get("model"),
                        api_base=litellm_params_dict.get("api_base"),
                        api_key=litellm_params_dict.get("api_key", "none"),
                        timeout=litellm_params_dict.get("timeout"),
                    )
                    
                    # Генерируем уникальный ID для модели
                    # Используем комбинацию model_name и api_base для уникальности
                    api_base = litellm_params_dict.get("api_base", "")
                    model_id = hashlib.sha256(f"{model_name}:{api_base}".encode()).hexdigest()
                    
                    # Создаём Deployment с уникальным ID
                    deployment = Deployment(
                        model_name=model_name,
                        litellm_params=litellm_params,
                        model_info=ModelInfo(id=model_id)
                    )
                    
                    # Добавляем модель в Router
                    result = proxy_server.llm_router.upsert_deployment(deployment)
                    
                    if was_existing:
                        updated_count += 1
                        logger.debug(f"Обновлена: {model_name}")
                    else:
                        added_count += 1
                        logger.debug(f"Добавлена: {model_name}")
                        
                except Exception as model_exc:
                    logger.error(f"Ошибка обновления модели {model.get('model_name')}: {model_exc}")
                    continue
            
            logger.info(f"Модели для провайдера {provider_name} обновлены: добавлено {added_count}, обновлено {updated_count}, удалено {deleted_count} моделей")
            
            # Логируем текущий список моделей
            current_models = proxy_server.llm_router.get_model_names()
            logger.info(f"Текущие модели в Router ({len(current_models)}):")
            for model_name in current_models:
                logger.info(f" {model_name}")

        except Exception as exc:
            logger.error(f"Критическая ошибка обновления: {exc}", exc_info=True)


def get_update_callback() -> callable:
    return update_models_in_router
