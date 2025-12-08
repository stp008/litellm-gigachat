"""
Команда start для запуска LiteLLM прокси-сервера для GigaChat.
"""

import click
import logging
import sys
from dotenv import load_dotenv

from ...proxy.server import (
    check_environment,
    check_dependencies,
    setup_certificates,
    setup_gigachat_integration,
    setup_model_sync,
    start_proxy_server
)


logger = logging.getLogger(__name__)


@click.command()
@click.option(
    '--host',
    default='0.0.0.0',
    help='Хост для прокси-сервера [default: 0.0.0.0]'
)
@click.option(
    '--port',
    type=int,
    default=4000,
    help='Порт для прокси-сервера [default: 4000]'
)
@click.option(
    '--config',
    default='config.yml',
    help='Путь к файлу конфигурации [default: config.yml]'
)
@click.pass_context
def start(ctx, host, port, config):
    """Запустить LiteLLM прокси-сервер для GigaChat."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 Host: {host}")
        click.echo(f"🔍 Port: {port}")
        click.echo(f"🔍 Config: {config}")
    
    # Загружаем переменные окружения
    load_dotenv()
    
    if not debug:
        click.echo("🚀 Запуск LiteLLM прокси-сервера для GigaChat")
        click.echo("=" * 50)
    
    # Выполняем все проверки через функции из server.py
    checks = [
        ("Переменные окружения", check_environment),
        ("Зависимости", check_dependencies),
        ("Сертификаты", setup_certificates),
        ("GigaChat интеграция", setup_gigachat_integration)
    ]
    
    for check_name, check_func in checks:
        if debug:
            logger.debug(f"Выполнение проверки: {check_name}")
        elif verbose:
            click.echo(f"📋 Проверка: {check_name}")
        
        try:
            if not check_func():
                if not verbose and not debug:
                    click.echo(f"❌ Ошибка при проверке: {check_name}")
                sys.exit(1)
            else:
                if verbose and not debug:
                    click.echo(f"  ✓ {check_name}: OK")
        except Exception as exc:
            logger.error(f"Ошибка проверки '{check_name}': {exc}")
            if debug:
                logger.debug(f"Check error details:", exc_info=True)
            if not verbose and not debug:
                click.echo(f"❌ Ошибка при проверке {check_name}: {exc}")
            sys.exit(1)
    
    if not debug:
        click.echo("✅ Все проверки пройдены, запуск сервера...")
        click.echo("=" * 50)
    
    # Запускаем сервер через функцию из server.py
    try:
        success = start_proxy_server(
            host=host,
            port=port,
            config_file=config,
            verbose=verbose,
            debug=debug
        )
        
        if success:
            if not debug:
                click.echo("✅ Сервер завершил работу")
        else:
            if not debug:
                click.echo("❌ Ошибка при работе сервера")
            sys.exit(1)
            
    except Exception as exc:
        logger.error(f"Ошибка запуска сервера: {exc}")
        if debug:
            logger.debug("Server start error details:", exc_info=True)
        if not verbose and not debug:
            click.echo(f"❌ Ошибка запуска сервера: {exc}")
        sys.exit(1)
