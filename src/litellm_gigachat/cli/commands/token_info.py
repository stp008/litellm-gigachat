"""
Команда token-info для показа информации о текущем токене.
"""

import click
import json
import logging
import sys
from datetime import datetime
from dotenv import load_dotenv

from ..utils import format_table
from ...core.token_manager import get_global_token_manager


logger = logging.getLogger(__name__)


def get_token_information() -> dict:
    """Получить информацию о токене."""
    try:
        token_manager = get_global_token_manager()
        
        # Получаем базовую информацию о токене
        token_info = token_manager.get_token_info()
        
        if not token_info:
            return {"error": "Токен не найден или недоступен"}
        
        # Дополняем информацию
        result = {
            "Статус токена": "Активен" if token_info.get("access_token") else "Неактивен",
            "Тип токена": token_info.get("token_type", "Bearer"),
            "Область действия": token_info.get("scope", "GIGACHAT_API_PERS"),
        }
        
        # Информация о времени
        if "expires_at" in token_info:
            expires_at = token_info["expires_at"]
            if isinstance(expires_at, str):
                try:
                    expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                except ValueError:
                    expires_at = expires_at
            
            if isinstance(expires_at, datetime):
                result["Истекает"] = expires_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                
                # Время до истечения
                now = datetime.now(expires_at.tzinfo) if expires_at.tzinfo else datetime.now()
                time_left = expires_at - now
                
                if time_left.total_seconds() > 0:
                    hours = int(time_left.total_seconds() // 3600)
                    minutes = int((time_left.total_seconds() % 3600) // 60)
                    result["Осталось времени"] = f"{hours}ч {minutes}м"
                    result["Статус"] = "Действителен"
                else:
                    result["Осталось времени"] = "Истек"
                    result["Статус"] = "Истек"
            else:
                result["Истекает"] = str(expires_at)
        
        if "expires_in" in token_info:
            expires_in = token_info["expires_in"]
            result["Время жизни"] = f"{expires_in} секунд"
        
        # Информация о создании
        if "created_at" in token_info:
            created_at = token_info["created_at"]
            if isinstance(created_at, str):
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    result["Создан"] = created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
                except ValueError:
                    result["Создан"] = str(created_at)
            else:
                result["Создан"] = str(created_at)
        
        # Дополнительная отладочная информация
        if logger.isEnabledFor(logging.DEBUG):
            result["Debug: Token preview"] = token_info.get("access_token", "")[:20] + "..."
            result["Debug: Raw expires_in"] = str(token_info.get("expires_in", "N/A"))
            result["Debug: Raw scope"] = str(token_info.get("scope", "N/A"))
        
        return result
        
    except Exception as exc:
        logger.error(f"Ошибка получения информации о токене: {exc}")
        logger.debug("Token info error details:", exc_info=True)
        return {"error": f"Ошибка: {exc}"}


def get_environment_info() -> dict:
    """Получить информацию об окружении."""
    import os
    
    env_info = {}
    
    # Переменные окружения GigaChat
    gigachat_vars = [
        "GIGACHAT_AUTH_KEY",
        "GIGACHAT_BASE_URL", 
        "GIGACHAT_SCOPE",
        "GIGACHAT_VERIFY_SSL_CERTS"
    ]
    
    for var in gigachat_vars:
        value = os.getenv(var)
        if value:
            if var == "GIGACHAT_AUTH_KEY":
                # Маскируем ключ
                env_info[var] = f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
            else:
                env_info[var] = value
        else:
            env_info[var] = "не установлена"
    
    return env_info


@click.command()
@click.option(
    '--format',
    type=click.Choice(['json', 'table']),
    default='table',
    help='Формат вывода [default: table]'
)
@click.pass_context
def token_info(ctx, format):
    """Показать информацию о текущем токене."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 Output format: {format}")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    try:
        # Получаем информацию о токене
        token_data = get_token_information()
        
        if "error" in token_data:
            click.echo(f"❌ {token_data['error']}", err=True)
            sys.exit(1)
        
        # Получаем информацию об окружении
        env_data = get_environment_info()
        
        if format == 'json':
            # JSON формат
            output = {
                "token_info": token_data,
                "environment": env_data,
                "timestamp": datetime.now().isoformat()
            }
            click.echo(json.dumps(output, ensure_ascii=False, indent=2))
            
        else:
            # Табличный формат
            if not debug:
                click.echo("🔑 Информация о токене GigaChat")
                click.echo("=" * 40)
            
            # Информация о токене
            click.echo(format_table(token_data, "Токен"))
            
            if verbose or debug:
                # Информация об окружении
                click.echo(format_table(env_data, "Переменные окружения"))
            
            # Статус
            status = token_data.get("Статус", "Неизвестно")
            if status == "Действителен":
                click.echo("\n✅ Токен действителен и готов к использованию")
            elif status == "Истек":
                click.echo("\n⚠️  Токен истек, требуется обновление")
                click.echo("Выполните: litellm-gigachat refresh-token")
            else:
                click.echo(f"\n❓ Статус токена: {status}")
    
    except Exception as exc:
        logger.error(f"Ошибка команды token-info: {exc}")
        if debug:
            logger.debug("Token-info command error details:", exc_info=True)
        click.echo(f"❌ Ошибка: {exc}", err=True)
        sys.exit(1)
