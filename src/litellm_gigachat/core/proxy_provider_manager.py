import os
import logging
from typing import Optional, Dict, List
from dataclasses import dataclass
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class ProxyProviderConfig:
    """Конфигурация одного прокси-провайдера"""
    name: str
    url: str
    auth_header: str
    auth_value: str
    suffix: str
    sync_enabled: bool = False
    sync_interval: int = 300
    timeout: int = 60
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Получение заголовков аутентификации"""
        if not self.auth_value:
            return {}
        return {self.auth_header: self.auth_value}
    
    def is_proxy_model(self, model_name: str) -> bool:
        """Проверка, принадлежит ли модель этому провайдеру"""
        return model_name.endswith(f"-{self.suffix}")


class MultiProxyProviderManager:
    """Менеджер для управления несколькими прокси-провайдерами"""
    
    def __init__(self):
        """Инициализация менеджера"""
        self.providers: List[ProxyProviderConfig] = []
    
    def load_from_config(self, config_path: str) -> bool:
        """
        Загрузка конфигурации провайдеров из YAML файла
        
        Args:
            config_path: Путь к файлу конфигурации
            
        Returns:
            True если конфигурация загружена успешно
        """
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                logger.warning(f"Файл конфигурации {config_path} не найден")
                return True
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                logger.warning("Пустой файл конфигурации")
                return True
            
            # Загружаем провайдеров из секции proxy_providers
            providers_config = config.get('proxy_providers', [])
            
            if not providers_config:
                logger.info("Секция proxy_providers не найдена в config.yml")
                return True
            
            # Парсим каждого провайдера
            for provider_data in providers_config:
                try:
                    provider = self._parse_provider_config(provider_data)
                    if provider:
                        self.providers.append(provider)
                        logger.info(f"Загружен провайдер: {provider.name} (суффикс: -{provider.suffix})")
                except Exception as exc:
                    logger.error(f"Ошибка парсинга провайдера {provider_data.get('name', 'unknown')}: {exc}")
            
            if not self.providers:
                logger.warning("Не удалось загрузить ни одного провайдера из config.yml")
                return True
            
            logger.info(f"Загружено {len(self.providers)} прокси-провайдеров")
            return True
            
        except Exception as exc:
            logger.error(f"Ошибка загрузки конфигурации провайдеров: {exc}")
            return True
    
    def _parse_provider_config(self, data: Dict) -> Optional[ProxyProviderConfig]:
        """
        Парсинг конфигурации одного провайдера
        
        Args:
            data: Словарь с данными провайдера
            
        Returns:
            ProxyProviderConfig или None при ошибке
        """
        name = data.get('name')
        url = data.get('url')
        auth_header = data.get('auth_header', 'X-Client-Id')
        auth_value = data.get('auth_value', '')
        suffix = data.get('suffix')
        
        if not name or not url or not suffix:
            logger.error(f"Провайдер должен содержать name, url и suffix: {data}")
            return None
        
        # Подстановка переменных окружения в auth_value
        auth_value = self._expand_env_vars(auth_value)
        
        if not auth_value:
            logger.warning(f"Провайдер {name}: auth_value пустой или переменная окружения не установлена")
        
        return ProxyProviderConfig(
            name=name,
            url=url.rstrip('/'),
            auth_header=auth_header,
            auth_value=auth_value,
            suffix=suffix,
            sync_enabled=data.get('sync_enabled', False),
            sync_interval=data.get('sync_interval', 300),
            timeout=data.get('timeout', 60)
        )
    
    def _expand_env_vars(self, value: str) -> str:
        """
        Подстановка переменных окружения в формате ${VAR_NAME}
        
        Args:
            value: Строка с возможными переменными окружения
            
        Returns:
            Строка с подставленными значениями
        """
        if not value or not isinstance(value, str):
            return value
        
        # Простая подстановка ${VAR_NAME}
        import re
        pattern = r'\$\{([^}]+)\}'
        
        def replace_var(match):
            var_name = match.group(1)
            return os.getenv(var_name, '')
        
        return re.sub(pattern, replace_var, value)
    
    def get_provider_by_suffix(self, model_name: str) -> Optional[ProxyProviderConfig]:
        """
        Поиск провайдера по суффиксу модели
        
        Args:
            model_name: Название модели
            
        Returns:
            ProxyProviderConfig или None если не найден
        """
        for provider in self.providers:
            if provider.is_proxy_model(model_name):
                return provider
        return None
    
    def get_provider_by_name(self, name: str) -> Optional[ProxyProviderConfig]:
        """
        Поиск провайдера по имени
        
        Args:
            name: Имя провайдера
            
        Returns:
            ProxyProviderConfig или None если не найден
        """
        for provider in self.providers:
            if provider.name == name:
                return provider
        return None
    
    def get_all_providers(self) -> List[ProxyProviderConfig]:
        """
        Получение списка всех провайдеров
        
        Returns:
            Список всех провайдеров
        """
        return self.providers.copy()
    
    def is_proxy_model(self, model_name: str) -> bool:
        """
        Проверка, является ли модель моделью прокси-провайдера
        
        Args:
            model_name: Название модели
            
        Returns:
            True если это модель прокси-провайдера
        """
        return self.get_provider_by_suffix(model_name) is not None
    
    def is_enabled(self) -> bool:
        """
        Проверка, включена ли поддержка прокси-провайдеров
        
        Returns:
            True если есть хотя бы один провайдер
        """
        return len(self.providers) > 0
    
    def validate_configuration(self) -> bool:
        """
        Валидация конфигурации всех провайдеров
        
        Returns:
            True если конфигурация корректна
        """
        if not self.providers:
            return True  # Нет провайдеров - валидация не нужна
        
        for provider in self.providers:
            if not provider.url:
                logger.error(f"Провайдер {provider.name}: URL не установлен")
                return False
            
            if not provider.auth_value:
                logger.error(f"Провайдер {provider.name}: auth_value не установлен")
                return False
        
        return True
    
    def get_configuration_info(self) -> Dict:
        """
        Получение информации о конфигурации для отладки
        
        Returns:
            Словарь с информацией о конфигурации
        """
        return {
            "enabled": self.is_enabled(),
            "providers_count": len(self.providers),
            "providers": [
                {
                    "name": p.name,
                    "url": p.url,
                    "suffix": p.suffix,
                    "sync_enabled": p.sync_enabled,
                    "has_auth_value": bool(p.auth_value)
                }
                for p in self.providers
            ],
            "is_valid": self.validate_configuration()
        }


# Глобальный экземпляр менеджера
_global_multi_proxy_provider_manager: Optional[MultiProxyProviderManager] = None


def get_global_multi_proxy_provider_manager() -> MultiProxyProviderManager:
    """Получение глобального экземпляра MultiProxyProviderManager"""
    global _global_multi_proxy_provider_manager
    if _global_multi_proxy_provider_manager is None:
        _global_multi_proxy_provider_manager = MultiProxyProviderManager()
    return _global_multi_proxy_provider_manager


def init_multi_proxy_provider_manager(config_path: str = "config.yml") -> MultiProxyProviderManager:
    """
    Инициализация глобального менеджера прокси-провайдеров
    
    Args:
        config_path: Путь к файлу конфигурации
        
    Returns:
        Инициализированный менеджер
    """
    manager = get_global_multi_proxy_provider_manager()
    manager.load_from_config(config_path)
    return manager
