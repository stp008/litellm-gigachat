import os
import logging
from typing import Optional, Dict
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

logger = logging.getLogger(__name__)

class InternalHeaderManager:
    """Менеджер для управления заголовками внутренней установки GigaChat"""
    
    def __init__(self):
        """
        Инициализация менеджера заголовков для внутренней установки
        """
        self.enabled = os.getenv("GIGACHAT_INTERNAL_ENABLED", "false").lower() == "true"
        self.url = os.getenv("GIGACHAT_INTERNAL_URL")
        self.header_name = os.getenv("GIGACHAT_AUTH_HEADER_NAME", "X-Client-Id")
        self.header_value = os.getenv("GIGACHAT_AUTH_HEADER_VALUE")
        self.model_suffix = os.getenv("GIGACHAT_INTERNAL_MODEL_SUFFIX", "internal")
        
        # Логирование конфигурации (без чувствительных данных)
        if self.enabled:
            logger.info("Internal GigaChat включен")
            logger.info(f"URL: {self.url}")
            logger.info(f"Header name: {self.header_name}")
            logger.info(f"Model suffix: {self.model_suffix}")
            logger.info(f"Header value: {'***' if self.header_value else 'НЕ УСТАНОВЛЕН'}")
        else:
            logger.debug("Internal GigaChat отключен")
    
    def get_auth_headers(self) -> Dict[str, str]:
        """
        Получение заголовков аутентификации для внутренней установки
        
        Returns:
            Словарь с заголовками аутентификации
        """
        if not self.enabled or not self.header_value:
            return {}
        
        return {self.header_name: self.header_value}
    
    def is_internal_model(self, model_name: str) -> bool:
        """
        Проверка, является ли модель внутренней моделью GigaChat
        
        Args:
            model_name: Название модели
            
        Returns:
            True если это внутренняя модель
        """
        if not self.enabled:
            return False
            
        return model_name.endswith(f"-{self.model_suffix}")
    
    def get_internal_url(self) -> Optional[str]:
        """
        Получение URL внутренней установки
        
        Returns:
            URL внутренней установки или None если отключена
        """
        return self.url if self.enabled else None
    
    def is_enabled(self) -> bool:
        """
        Проверка, включена ли поддержка внутренней установки
        
        Returns:
            True если внутренняя установка включена
        """
        return self.enabled
    
    def validate_configuration(self) -> bool:
        """
        Валидация конфигурации внутренней установки
        
        Returns:
            True если конфигурация корректна
        """
        if not self.enabled:
            return True  # Если отключена, то валидация не нужна
        
        if not self.url:
            logger.error("GIGACHAT_INTERNAL_URL не установлен")
            return False
        
        if not self.header_value:
            logger.error("GIGACHAT_AUTH_HEADER_VALUE не установлен")
            return False
        
        if not self.header_name:
            logger.error("GIGACHAT_AUTH_HEADER_NAME не установлен")
            return False
        
        return True
    
    def get_model_names(self) -> list[str]:
        """
        Получение списка названий внутренних моделей
        
        Returns:
            Список названий моделей с суффиксом
        """
        if not self.enabled:
            return []
        
        base_models = ["gigachat", "gigachat-pro", "gigachat-max"]
        return [f"{model}-{self.model_suffix}" for model in base_models]
    
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
            "available_models": self.get_model_names(),
            "is_valid": self.validate_configuration()
        }


# Глобальный экземпляр менеджера заголовков
_global_internal_header_manager: Optional[InternalHeaderManager] = None

def get_global_internal_header_manager() -> InternalHeaderManager:
    """Получение глобального экземпляра InternalHeaderManager"""
    global _global_internal_header_manager
    if _global_internal_header_manager is None:
        _global_internal_header_manager = InternalHeaderManager()
    return _global_internal_header_manager

def get_internal_auth_headers() -> Dict[str, str]:
    """Удобная функция для получения заголовков аутентификации внутренней установки"""
    return get_global_internal_header_manager().get_auth_headers()

def is_internal_gigachat_enabled() -> bool:
    """Удобная функция для проверки, включена ли внутренняя установка"""
    return get_global_internal_header_manager().is_enabled()
