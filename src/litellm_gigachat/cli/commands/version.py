"""
Команда version для показа версии пакета и компонентов.
"""

import click
import json
import logging
import sys
from datetime import datetime

from ..utils import get_package_version, get_component_versions, format_table


logger = logging.getLogger(__name__)


def get_detailed_version_info() -> dict:
    """Получить детальную информацию о версиях."""
    info = {
        "package": {
            "name": "litellm-gigachat",
            "version": get_package_version(),
            "timestamp": datetime.now().isoformat()
        },
        "components": get_component_versions()
    }
    
    # Дополнительная системная информация
    import platform
    import os
    
    info["system"] = {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "architecture": platform.architecture()[0],
        "machine": platform.machine(),
        "processor": platform.processor() or "unknown"
    }
    
    # Информация об окружении
    info["environment"] = {
        "python_path": sys.executable,
        "working_directory": os.getcwd(),
        "user": os.getenv("USER") or os.getenv("USERNAME") or "unknown"
    }
    
    return info


def format_version_output(info: dict, show_components: bool = False) -> str:
    """Форматировать вывод версии."""
    lines = []
    
    # Основная информация о пакете
    package_info = info["package"]
    lines.append(f"📦 {package_info['name']} v{package_info['version']}")
    
    if show_components:
        lines.append("")
        lines.append("🔧 Компоненты:")
        lines.append("-" * 40)
        
        components = info["components"]
        for name, version in components.items():
            status = "✓" if version != "not installed" else "✗"
            lines.append(f"  {status} {name}: {version}")
        
        lines.append("")
        lines.append("💻 Система:")
        lines.append("-" * 40)
        
        system_info = info["system"]
        lines.append(f"  Platform: {system_info['platform']}")
        lines.append(f"  Python: {system_info['python_version']} ({system_info['python_implementation']})")
        lines.append(f"  Architecture: {system_info['architecture']}")
        lines.append(f"  Machine: {system_info['machine']}")
        
        if system_info['processor'] != "unknown":
            lines.append(f"  Processor: {system_info['processor']}")
        
        lines.append("")
        lines.append("🌍 Окружение:")
        lines.append("-" * 40)
        
        env_info = info["environment"]
        lines.append(f"  Python path: {env_info['python_path']}")
        lines.append(f"  Working dir: {env_info['working_directory']}")
        lines.append(f"  User: {env_info['user']}")
    
    return "\n".join(lines)


def check_updates() -> dict:
    """Проверить доступность обновлений (заглушка)."""
    # В будущем здесь можно добавить проверку PyPI
    return {
        "update_available": False,
        "latest_version": None,
        "message": "Проверка обновлений недоступна"
    }


@click.command()
@click.option(
    '--components',
    is_flag=True,
    help='Показать версии всех компонентов'
)
@click.option(
    '--json-output',
    is_flag=True,
    help='Вывод в формате JSON'
)
@click.option(
    '--check-updates',
    is_flag=True,
    help='Проверить доступность обновлений'
)
@click.pass_context
def version_cmd(ctx, components, json_output, check_updates):
    """Показать версию пакета и компонентов."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 Show components: {components}")
        click.echo(f"🔍 JSON output: {json_output}")
        click.echo(f"🔍 Check updates: {check_updates}")
    
    try:
        # Получаем информацию о версиях
        version_info = get_detailed_version_info()
        
        if debug:
            logger.debug(f"Version info collected: {version_info}")
        
        if json_output:
            # JSON формат
            output = version_info.copy()
            
            if check_updates:
                output["updates"] = check_updates()
            
            click.echo(json.dumps(output, ensure_ascii=False, indent=2))
        
        else:
            # Обычный формат
            if not debug:
                click.echo("ℹ️  Информация о версии")
                click.echo("=" * 30)
            
            # Основная информация
            output = format_version_output(version_info, components or verbose or debug)
            click.echo(output)
            
            # Проверка обновлений
            if check_updates:
                click.echo("")
                click.echo("🔄 Проверка обновлений:")
                click.echo("-" * 30)
                
                update_info = check_updates()
                if update_info["update_available"]:
                    click.echo(f"✨ Доступна новая версия: {update_info['latest_version']}")
                    click.echo("Обновите: pip install --upgrade litellm-gigachat")
                else:
                    click.echo("✅ Установлена последняя версия")
                
                if update_info["message"]:
                    click.echo(f"ℹ️  {update_info['message']}")
            
            # Дополнительная информация в verbose режиме
            if verbose and not components:
                click.echo("")
                click.echo("📋 Дополнительная информация:")
                click.echo("-" * 30)
                
                components_table = {}
                for name, version in version_info["components"].items():
                    components_table[name] = version
                
                click.echo(format_table(components_table, "Компоненты"))
    
    except Exception as exc:
        logger.error(f"Ошибка команды version: {exc}")
        if debug:
            logger.debug("Version command error details:", exc_info=True)
        click.echo(f"❌ Ошибка: {exc}", err=True)
        sys.exit(1)
