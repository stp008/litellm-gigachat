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
        self._legacy_mode = False
    
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
                return self._load_legacy_config()
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            if not config:
                logger.warning("Пустой файл конфигурации")
                return self._load_legacy_config()
            
            # Загружаем провайдеров из секции proxy_providers
            providers_config = config.get('proxy_providers', [])
            
            if not providers_config:
                logger.info("Секция proxy_providers не найдена в config.yml, используем legacy режим")
                return self._load_legacy_config()
            
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
                return self._load_legacy_config()
            
            logger.info(f"Загружено {len(self.providers)} прокси-провайдеров")
            return True
            
        except Exception as exc:
            logger.error(f"Ошибка загрузки конфигурации провайдеров: {exc}")
            return self._load_legacy_config()
    
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
    
    def _load_legacy_config(self) -> bool:
        """
        Загрузка конфигурации из старых переменных окружения (обратная совместимость)
        
        Returns:
            True если legacy конфигурация загружена
        """
        enabled = os.getenv("PROXY_PROVIDER_ENABLED", "false").lower() == "true"
        
        if not enabled:
            logger.info("Прокси-провайдеры отключены (PROXY_PROVIDER_ENABLED=false)")
            return True
        
        url = os.getenv("PROXY_PROVIDER_URL")
        auth_header = os.getenv("PROXY_PROVIDER_AUTH_HEADER", "X-Client-Id")
        auth_value = os.getenv("PROXY_PROVIDER_AUTH_VALUE")
        suffix = os.getenv("PROXY_PROVIDER_MODEL_SUFFIX", "proxy")
        
        if not url or not auth_value:
            logger.error("Legacy режим: PROXY_PROVIDER_URL и PROXY_PROVIDER_AUTH_VALUE должны быть установлены")
            return False
        
        # Создаём legacy провайдера
        legacy_provider = ProxyProviderConfig(
            name="legacy-provider",
            url=url.rstrip('/'),
            auth_header=auth_header,
            auth_value=auth_value,
            suffix=suffix,
            sync_enabled=os.getenv("MODEL_SYNC_ENABLED", "false").lower() == "true",
            sync_interval=int(os.getenv("MODEL_SYNC_INTERVAL", "300")),
            timeout=int(os.getenv("GIGACHAT_TIMEOUT", "60"))
        )
        
        self.providers.append(legacy_provider)
        self._legacy_mode = True
        
        logger.info("✓ Загружен legacy прокси-провайдер из переменных окружения")
        logger.info(f"  URL: {url}")
        logger.info(f"  Суффикс: -{suffix}")
        
        return True
    
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
    
    def is_legacy_mode(self) -> bool:
        """
        Проверка, работает ли менеджер в legacy режиме
        
        Returns:
            True если используется legacy конфигурация
        """
        return self._legacy_mode
    
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
            "legacy_mode": self._legacy_mode,
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


# ============================================================================
# Legacy API для обратной совместимости
# ============================================================================

class ProxyProviderManager:
    """
    Legacy класс для обратной совместимости.
    Теперь является оберткой над MultiProxyProviderManager.
    """
    
    def __init__(self):
        """Инициализация legacy менеджера"""
        self.multi_manager = get_global_multi_proxy_provider_manager()
        
        # Legacy поля для совместимости
        if self.multi_manager.providers:
            first_provider = self.multi_manager.providers[0]
            self.enabled = True
            self.url = first_provider.url
            self.header_name = first_provider.auth_header
            self.header_value = first_provider.auth_value
            self.model_suffix = first_provider.suffix
        else:
            self.enabled = False
            self.url = None
            self.header_name = "X-Client-Id"
            self.header_value = None
            self.model_suffix = "proxy"
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Legacy метод - возвращает заголовки первого провайдера"""
        if self.multi_manager.providers:
            return self.multi_manager.providers[0].get_auth_headers()
        return {}
    
    def is_proxy_model(self, model_name: str) -> bool:
        """Legacy метод - проверка через multi_manager"""
        return self.multi_manager.is_proxy_model(model_name)
    
    def get_provider_url(self) -> Optional[str]:
        """Legacy метод - возвращает URL первого провайдера"""
        return self.url if self.enabled else None
    
    def is_enabled(self) -> bool:
        """Legacy метод"""
        return self.enabled
    
    def get_model_suffix(self) -> str:
        """Legacy метод"""
        return self.model_suffix
    
    def validate_configuration(self) -> bool:
        """Legacy метод"""
        return self.multi_manager.validate_configuration()
    
    def get_configuration_info(self) -> Dict:
        """Legacy метод"""
        return self.multi_manager.get_configuration_info()


def get_global_proxy_provider_manager() -> ProxyProviderManager:
    """Legacy функция для обратной совместимости"""
    return ProxyProviderManager()


def get_proxy_auth_headers() -> Dict[str, str]:
    """Legacy функция для обратной совместимости"""
    return get_global_proxy_provider_manager().get_auth_headers()


def is_proxy_provider_enabled() -> bool:
    """Legacy функция для обратной совместимости"""
    return get_global_proxy_provider_manager().is_enabled()
