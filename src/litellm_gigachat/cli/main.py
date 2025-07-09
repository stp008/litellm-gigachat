#!/usr/bin/env python3
"""
Главный CLI модуль для litellm-gigachat.
"""

import click
import sys

from .commands.start import start
from .commands.test import test
from .commands.token_info import token_info
from .commands.refresh_token import refresh_token
from .commands.examples import examples
from .commands.version import version_cmd
from .commands.help_examples import help_examples
from .commands.env_check import env_check
from .utils import setup_logging, get_package_version


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Показать версию и выйти')
@click.option('-v', '--verbose', is_flag=True, help='Подробная информация о выполнении')
@click.option('-d', '--debug', is_flag=True, help='Максимальная отладка с сохранением логов')
@click.pass_context
def cli(ctx, version, verbose, debug):
    """LiteLLM прокси-сервер для GigaChat API.
    
    Для получения справки по конкретной команде используйте:
    litellm-gigachat COMMAND --help
    """
    
    # Создаем контекст для передачи параметров в подкоманды
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    ctx.obj['debug'] = debug
    
    # Настройка логирования
    setup_logging(verbose, debug)
    
    if version:
        click.echo(f"litellm-gigachat {get_package_version()}")
        ctx.exit()
    
    # Если команда не указана, показываем help
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Добавляем команды
cli.add_command(start)
cli.add_command(test)
cli.add_command(token_info)
cli.add_command(refresh_token)
cli.add_command(examples)
cli.add_command(version_cmd, name='version')
cli.add_command(help_examples, name='help-examples')
cli.add_command(env_check, name='env-check')


def main():
    """Точка входа для CLI."""
    try:
        cli()
    except KeyboardInterrupt:
        click.echo("\n⚠️  Прервано пользователем", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Ошибка: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
