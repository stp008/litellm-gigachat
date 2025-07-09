"""
Команда help-examples для показа примеров использования.
"""

import click


@click.command()
@click.pass_context
def help_examples(ctx):
    """Показать примеры использования команд."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
    
    if not debug:
        click.echo("🚀 ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ")
        click.echo("=" * 50)
    
    examples = [
        ("Запуск сервера", [
            "litellm-gigachat start",
            "litellm-gigachat start --host localhost --port 8080",
            "litellm-gigachat start --config my-config.yml"
        ]),
        ("Тестирование", [
            "litellm-gigachat test",
            "litellm-gigachat --verbose test --timeout 60",
            "litellm-gigachat --debug test"
        ]),
        ("Управление токенами", [
            "litellm-gigachat token-info",
            "litellm-gigachat token-info --format json",
            "litellm-gigachat refresh-token --force"
        ]),
        ("Примеры и версия", [
            "litellm-gigachat examples --list",
            "litellm-gigachat examples --run basic_usage",
            "litellm-gigachat version --components"
        ]),
        ("Режимы работы", [
            "litellm-gigachat start                    # Обычный режим",
            "litellm-gigachat --verbose start         # Подробный вывод",
            "litellm-gigachat --debug start           # Максимальная отладка"
        ])
    ]
    
    for category, commands in examples:
        click.echo(f"\n📋 {category}:")
        for cmd in commands:
            click.echo(f"  {cmd}")
    
    click.echo(f"\n💡 Для получения справки по конкретной команде:")
    click.echo(f"  litellm-gigachat COMMAND --help")
