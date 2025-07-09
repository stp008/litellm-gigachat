"""
Команда refresh-token для принудительного обновления токена.
"""

import click
import logging
import sys
import time
from dotenv import load_dotenv

from ...core.token_manager import get_global_token_manager


logger = logging.getLogger(__name__)


def refresh_token_force(force: bool = False) -> bool:
    """Принудительно обновить токен."""
    try:
        token_manager = get_global_token_manager()
        
        # Получаем текущую информацию о токене
        current_info = token_manager.get_token_info()
        
        if current_info and not force:
            # Проверяем, нужно ли обновлять токен
            expires_in = current_info.get("expires_in", 0)
            if expires_in > 300:  # Если токен действителен еще больше 5 минут
                logger.info(f"Текущий токен еще действителен ({expires_in} секунд)")
                logger.info("Используйте --force для принудительного обновления")
                return False
        
        logger.info("Обновление токена...")
        start_time = time.time()
        
        # Принудительно обновляем токен
        if hasattr(token_manager, 'refresh_token'):
            success = token_manager.refresh_token()
        else:
            # Если метода refresh_token нет, получаем новый токен
            token_manager._token = None  # Сбрасываем кэш
            token = token_manager.get_token()
            success = bool(token)
        
        end_time = time.time()
        
        if success:
            # Получаем информацию о новом токене
            new_info = token_manager.get_token_info()
            
            logger.info(f"✓ Токен успешно обновлен за {end_time - start_time:.2f}s")
            
            if new_info:
                expires_in = new_info.get("expires_in", 0)
                logger.info(f"✓ Новый токен действителен {expires_in} секунд")
                
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"New token info: {new_info}")
            
            return True
        else:
            logger.error("✗ Не удалось обновить токен")
            return False
            
    except Exception as exc:
        logger.error(f"✗ Ошибка обновления токена: {exc}")
        logger.debug("Token refresh error details:", exc_info=True)
        return False


def validate_environment() -> bool:
    """Проверить переменные окружения перед обновлением токена."""
    import os
    
    if not os.getenv("GIGACHAT_AUTH_KEY"):
        logger.error("Переменная GIGACHAT_AUTH_KEY не установлена")
        logger.error("Установите: export GIGACHAT_AUTH_KEY='ваш_ключ'")
        return False
    
    logger.debug("Environment validation passed")
    return True


@click.command()
@click.option(
    '--force',
    is_flag=True,
    help='Принудительно обновить токен даже если текущий еще действителен'
)
@click.pass_context
def refresh_token(ctx, force):
    """Принудительно обновить токен."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 Force refresh: {force}")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    if not debug:
        click.echo("🔄 Обновление токена GigaChat")
        click.echo("=" * 30)
    
    # Проверяем окружение
    if not validate_environment():
        click.echo("❌ Ошибка конфигурации окружения", err=True)
        sys.exit(1)
    
    try:
        # Показываем текущую информацию о токене
        if verbose or debug:
            logger.info("Получение информации о текущем токене...")
            
            token_manager = get_global_token_manager()
            current_info = token_manager.get_token_info()
            
            if current_info:
                expires_in = current_info.get("expires_in", 0)
                logger.info(f"Текущий токен действителен: {expires_in} секунд")
                
                if debug:
                    logger.debug(f"Current token info: {current_info}")
            else:
                logger.info("Текущий токен отсутствует или недействителен")
        
        # Выполняем обновление
        if refresh_token_force(force):
            if not debug:
                click.echo("✅ Токен успешно обновлен")
            
            if verbose or debug:
                # Показываем информацию о новом токене
                token_manager = get_global_token_manager()
                new_info = token_manager.get_token_info()
                
                if new_info:
                    expires_in = new_info.get("expires_in", 0)
                    hours = expires_in // 3600
                    minutes = (expires_in % 3600) // 60
                    
                    logger.info(f"Новый токен действителен: {hours}ч {minutes}м")
        else:
            if not debug:
                click.echo("❌ Не удалось обновить токен", err=True)
            sys.exit(1)
    
    except Exception as exc:
        logger.error(f"Ошибка команды refresh-token: {exc}")
        if debug:
            logger.debug("Refresh-token command error details:", exc_info=True)
        click.echo(f"❌ Ошибка: {exc}", err=True)
        sys.exit(1)
