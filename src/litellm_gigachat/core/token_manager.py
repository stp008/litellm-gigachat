import os
import time
import threading
import uuid
import requests
from typing import Optional
import logging
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

logger = logging.getLogger(__name__)

class TokenManager:
    """Менеджер для автоматического управления токенами GigaChat API"""
    
    def __init__(self, auth_key: Optional[str] = None, scope: str = "GIGACHAT_API_PERS"):
        """
        Инициализация менеджера токенов
        
        Args:
            auth_key: Authorization key в формате Base64. Если не указан, берется из GIGACHAT_AUTH_KEY
            scope: Область действия токена
        """
        self.auth_key = auth_key or os.environ.get("GIGACHAT_AUTH_KEY")
        if not self.auth_key:
            raise ValueError("Authorization key не найден. Установите GIGACHAT_AUTH_KEY или передайте auth_key")
        
        self.scope = scope
        self.token_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        
        # Состояние токена
        self._current_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._lock = threading.Lock()
        
        # Буфер времени для обновления токена (5 минут до истечения)
        self.refresh_buffer_seconds = 300
        
    def _request_new_token(self) -> tuple[str, float]:
        """
        Запрос нового токена от API
        
        Returns:
            Tuple[token, expires_at_timestamp]
        """
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "RqUID": str(uuid.uuid4()),
            "Authorization": f"Basic {self.auth_key}",
        }
        
        data = {"scope": self.scope}
        
        try:
            logger.info("Запрос нового токена GigaChat...")
            response = requests.post(
                self.token_url,
                headers=headers,
                data=data,
                timeout=20,
            )
            response.raise_for_status()
            
            token_data = response.json()
            access_token = token_data["access_token"]
            
            # Вычисляем время истечения (токен живет 30 минут)
            expires_at = time.time() + (30 * 60)  # 30 минут в секундах
            
            logger.info("Новый токен успешно получен")
            return access_token, expires_at
            
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении токена: {e}")
            raise
        except KeyError as e:
            logger.error(f"Неожиданный формат ответа API: {e}")
            raise
    
    def _is_token_expired(self) -> bool:
        """Проверка, истек ли токен (с учетом буфера)"""
        if not self._current_token:
            return True
        
        # Считаем токен истекшим за 5 минут до реального истечения
        return time.time() >= (self._token_expires_at - self.refresh_buffer_seconds)
    
    def get_token(self, force_refresh: bool = False) -> str:
        """
        Получение актуального токена (с автоматическим обновлением при необходимости)
        
        Args:
            force_refresh: Принудительное обновление токена
            
        Returns:
            Актуальный access token
        """
        with self._lock:
            if force_refresh or self._is_token_expired():
                try:
                    self._current_token, self._token_expires_at = self._request_new_token()
                except Exception as e:
                    if self._current_token and not force_refresh:
                        # Если есть старый токен и это не принудительное обновление,
                        # попробуем использовать его
                        logger.warning(f"Не удалось обновить токен, используем старый: {e}")
                        return self._current_token
                    else:
                        raise
            
            return self._current_token
    
    def invalidate_token(self):
        """Принудительная инвалидация текущего токена"""
        with self._lock:
            self._current_token = None
            self._token_expires_at = 0
            logger.info("Токен инвалидирован")
    
    def get_token_info(self) -> dict:
        """Получение информации о текущем токене"""
        with self._lock:
            return {
                "has_token": bool(self._current_token),
                "expires_at": self._token_expires_at,
                "expires_in_seconds": max(0, self._token_expires_at - time.time()) if self._token_expires_at else 0,
                "is_expired": self._is_token_expired()
            }


# Глобальный экземпляр менеджера токенов
_global_token_manager: Optional[TokenManager] = None

def get_global_token_manager() -> TokenManager:
    """Получение глобального экземпляра TokenManager"""
    global _global_token_manager
    if _global_token_manager is None:
        _global_token_manager = TokenManager()
    return _global_token_manager

def get_gigachat_token() -> str:
    """Удобная функция для получения актуального токена GigaChat"""
    return get_global_token_manager().get_token()
