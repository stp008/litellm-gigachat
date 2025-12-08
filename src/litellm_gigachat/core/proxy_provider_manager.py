import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

logger = logging.getLogger(__name__)

class ProxyProviderManager:
    """Менеджер для управления заголовками прокси-провайдера (кастомный API endpoint)"""
    
    def __init__(self):
        """
        Инициализация менеджера заголовков для прокси-провайдера
        """
        self.enabled = os.getenv("PROXY_PROVIDER_ENABLED", "false").lower() == "true"
        self.url = os.getenv("PROXY_PROVIDER_URL")
        self.header_name = os.getenv("PROXY_PROVIDER_AUTH_HEADER", "X-Client-Id")
        self.header_value = os.getenv("PROXY_PROVIDER_AUTH_VALUE")
        self.model_suffix = os.getenv("PROXY_PROVIDER_MODEL_SUFFIX", "proxy")
        
        # Логирование конфигурации (без чувствительных данных)
        if self.enabled:
            logger.info("Прокси-провайдер включен")
            logger.info(f"URL: {self.url}")
            logger.info(f"Header name: {self.header_name}")
            logger.info(f"Model suffix: {self.model_suffix}")
            logger.info(f"Header value: {'***' if self.header_value else 'НЕ УСТАНОВЛЕН'}")
        else:
            logger.debug("Прокси-провайдер отключен")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Получение заголовков аутентификации для прокси-провайдера
        
        Returns:
            Словарь с заголовками аутентификации
        """
        if not self.enabled or not self.header_value:
            return {}
        
        return {self.header_name: self.header_value}
    
    def is_proxy_model(self, model_name: str) -> bool:
        """
        Проверка, является ли модель моделью прокси-провайдера
        
        Args:
            model_name: Название модели
            
        Returns:
            True если это модель прокси-провайдера
        """
        if not self.enabled:
            return False
            
        return model_name.endswith(f"-{self.model_suffix}")
    
    def get_provider_url(self) -> Optional[str]:
        """
        Получение URL прокси-провайдера
        
        Returns:
            URL прокси-провайдера или None если отключен
        """
        return self.url if self.enabled else None
    
    def is_enabled(self) -> bool:
        """
        Проверка, включена ли поддержка прокси-провайдера
        
        Returns:
            True если прокси-провайдер включен
        """
        return self.enabled
    
    def get_model_suffix(self) -> str:
        """
        Получение суффикса для моделей прокси-провайдера
        
        Returns:
            Суффикс модели
        """
        return self.model_suffix
    
    def validate_configuration(self) -> bool:
        """
        Валидация конфигурации прокси-провайдера
        
        Returns:
            True если конфигурация корректна
        """
        if not self.enabled:
            return True  # Если отключен, то валидация не нужна
        
        if not self.url:
            logger.error("PROXY_PROVIDER_URL не установлен")
            return False
        
        if not self.header_value:
            logger.error("PROXY_PROVIDER_AUTH_VALUE не установлен")
            return False
        
        if not self.header_name:
            logger.error("PROXY_PROVIDER_AUTH_HEADER не установлен")
            return False
        
        return True
    
    def get_configuration_info(self) -> Dict[str, any]:
        """
        Получение информации о конфигурации для отладки
        
        Returns:
            Словарь с информацией о конфигурации
        """
        return {
            "enabled": self.enabled,
            "url": self.url,
            "header_name": self.header_name,
            "has_header_value": bool(self.header_value),
            "model_suffix": self.model_suffix,
            "is_valid": self.validate_configuration()
        }


# Глобальный экземпляр менеджера заголовков
_global_proxy_provider_manager: Optional[ProxyProviderManager] = None

def get_global_proxy_provider_manager() -> ProxyProviderManager:
    """Получение глобального экземпляра ProxyProviderManager"""
    global _global_proxy_provider_manager
    if _global_proxy_provider_manager is None:
        _global_proxy_provider_manager = ProxyProviderManager()
    return _global_proxy_provider_manager

def get_proxy_auth_headers() -> Dict[str, str]:
    """Удобная функция для получения заголовков аутентификации прокси-провайдера"""
    return get_global_proxy_provider_manager().get_auth_headers()

def is_proxy_provider_enabled() -> bool:
    """Удобная функция для проверки, включен ли прокси-провайдер"""
    return get_global_proxy_provider_manager().is_enabled()
