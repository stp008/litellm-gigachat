"""
Команда env-check для проверки переменных окружения.
"""

import click
import os
import sys
from dotenv import load_dotenv

from ..utils import format_table


@click.command()
@click.option(
    '--format',
    type=click.Choice(['json', 'table']),
    default='table',
    help='Формат вывода [default: table]'
)
@click.pass_context
def env_check(ctx, format):
    """Проверить переменные окружения и их статус."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 Output format: {format}")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    if not debug:
        click.echo("🌍 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ")
        click.echo("=" * 40)
    
    # Определяем переменные для проверки
    env_vars = {
        "GIGACHAT_AUTH_KEY": {
            "description": "Ключ авторизации (обязательно)",
            "required": True,
            "mask": True
        },
        "GIGACHAT_BASE_URL": {
            "description": "URL API (опционально)",
            "required": False,
            "mask": False
        },
        "GIGACHAT_SCOPE": {
            "description": "Область действия токена",
            "required": False,
            "mask": False
        },
        "GIGACHAT_VERIFY_SSL_CERTS": {
            "description": "Проверка SSL сертификатов",
            "required": False,
            "mask": False
        }
    }
    
    # Проверяем переменные
    results = {}
    missing_required = []
    
    for var_name, var_info in env_vars.items():
        value = os.getenv(var_name)
        
        if value:
            if var_info["mask"]:
                # Маскируем чувствительные данные
                if len(value) > 14:
                    display_value = f"{value[:10]}...{value[-4:]}"
                else:
                    display_value = "***"
            else:
                display_value = value
            
            status = "✓ установлена"
            results[var_name] = f"{status} ({display_value})"
        else:
            status = "✗ не установлена"
            results[var_name] = status
            
            if var_info["required"]:
                missing_required.append(var_name)
    
    # Выводим результаты
    if format == 'json':
        import json
        output = {
            "environment_variables": results,
            "missing_required": missing_required,
            "status": "ok" if not missing_required else "error"
        }
        click.echo(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        # Табличный формат
        click.echo(format_table(results, "Переменные окружения"))
        
        # Описания переменных
        if verbose or debug:
            click.echo("\n📋 Описания переменных:")
            click.echo("-" * 30)
            for var_name, var_info in env_vars.items():
                required_text = " (обязательно)" if var_info["required"] else " (опционально)"
                click.echo(f"  {var_name}: {var_info['description']}{required_text}")
        
        # Статус проверки
        click.echo()
        if missing_required:
            click.echo("❌ Отсутствуют обязательные переменные:")
            for var in missing_required:
                click.echo(f"  - {var}")
            click.echo()
            click.echo("💡 Установите переменные окружения:")
            click.echo("  export GIGACHAT_AUTH_KEY='ваш_ключ'")
            click.echo("  # или создайте файл .env в корне проекта")
            sys.exit(1)
        else:
            click.echo("✅ Все обязательные переменные установлены")
            
            # Дополнительные рекомендации
            if verbose or debug:
                click.echo()
                click.echo("💡 Дополнительные настройки:")
                if not os.getenv("GIGACHAT_BASE_URL"):
                    click.echo("  - GIGACHAT_BASE_URL: будет использован по умолчанию")
                if not os.getenv("GIGACHAT_SCOPE"):
                    click.echo("  - GIGACHAT_SCOPE: будет использован GIGACHAT_API_PERS")
