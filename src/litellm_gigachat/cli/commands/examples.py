"""
Команда examples для запуска интерактивных примеров использования.
"""

import click
import logging
import os
import sys
from pathlib import Path
from importlib import import_module

from ..utils import format_table


logger = logging.getLogger(__name__)


def get_examples_directory() -> Path:
    """Найти директорию с примерами."""
    # Ищем директорию examples относительно корня проекта
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent.parent
    examples_dir = project_root / "examples"
    
    if examples_dir.exists():
        return examples_dir
    
    # Альтернативный поиск
    for parent in current_file.parents:
        potential_examples = parent / "examples"
        if potential_examples.exists():
            return potential_examples
    
    # Если не найдено, возвращаем ожидаемый путь
    return examples_dir


def discover_examples() -> dict:
    """Найти все доступные примеры."""
    examples_dir = get_examples_directory()
    examples = {}
    
    if not examples_dir.exists():
        logger.warning(f"Директория примеров не найдена: {examples_dir}")
        return examples
    
    # Ищем Python файлы в директории examples
    for file_path in examples_dir.glob("*.py"):
        if file_path.name.startswith("__"):
            continue
        
        example_name = file_path.stem
        
        # Пытаемся получить описание из docstring
        try:
            spec = import_module(f"examples.{example_name}")
            description = spec.__doc__ or "Описание недоступно"
            description = description.strip().split('\n')[0]  # Первая строка
        except Exception:
            description = "Описание недоступно"
        
        examples[example_name] = {
            "file": file_path,
            "description": description,
            "module": f"examples.{example_name}"
        }
    
    return examples


def run_example(example_name: str) -> bool:
    """Запустить конкретный пример."""
    examples = discover_examples()
    
    if example_name not in examples:
        logger.error(f"Пример '{example_name}' не найден")
        return False
    
    example_info = examples[example_name]
    
    try:
        logger.info(f"Запуск примера: {example_name}")
        logger.info(f"Описание: {example_info['description']}")
        logger.info(f"Файл: {example_info['file']}")
        
        # Добавляем путь к примерам в sys.path
        examples_dir = get_examples_directory()
        if str(examples_dir.parent) not in sys.path:
            sys.path.insert(0, str(examples_dir.parent))
        
        # Импортируем и запускаем модуль
        module = import_module(example_info['module'])
        
        # Ищем функцию main
        if hasattr(module, 'main'):
            logger.info("Выполнение функции main()...")
            result = module.main()
            logger.info("Пример выполнен успешно")
            return True
        else:
            logger.warning("Функция main() не найдена в примере")
            logger.info("Модуль импортирован, но не выполнен")
            return True
            
    except Exception as exc:
        logger.error(f"Ошибка выполнения примера '{example_name}': {exc}")
        logger.debug("Example execution error details:", exc_info=True)
        return False


def run_interactive_examples() -> None:
    """Запустить интерактивный режим выбора примеров."""
    examples = discover_examples()
    
    if not examples:
        click.echo("❌ Примеры не найдены")
        return
    
    click.echo("📚 Доступные примеры:")
    click.echo("=" * 40)
    
    # Показываем список примеров
    for i, (name, info) in enumerate(examples.items(), 1):
        click.echo(f"{i}. {name}")
        click.echo(f"   {info['description']}")
        click.echo()
    
    # Интерактивный выбор
    while True:
        try:
            choice = click.prompt(
                f"Выберите пример (1-{len(examples)}) или 'q' для выхода",
                type=str
            )
            
            if choice.lower() in ['q', 'quit', 'exit']:
                click.echo("👋 До свидания!")
                break
            
            try:
                choice_num = int(choice)
                if 1 <= choice_num <= len(examples):
                    example_name = list(examples.keys())[choice_num - 1]
                    
                    click.echo(f"\n🚀 Запуск примера: {example_name}")
                    click.echo("-" * 30)
                    
                    if run_example(example_name):
                        click.echo("✅ Пример выполнен успешно")
                    else:
                        click.echo("❌ Ошибка выполнения примера")
                    
                    click.echo("-" * 30)
                    
                    # Спрашиваем, хочет ли пользователь запустить еще один пример
                    if not click.confirm("Запустить еще один пример?"):
                        break
                else:
                    click.echo(f"❌ Неверный выбор. Введите число от 1 до {len(examples)}")
            except ValueError:
                click.echo("❌ Неверный ввод. Введите число или 'q' для выхода")
                
        except (KeyboardInterrupt, EOFError):
            click.echo("\n👋 До свидания!")
            break


@click.command()
@click.option(
    '--list',
    'list_examples',
    is_flag=True,
    help='Показать список доступных примеров'
)
@click.option(
    '--run',
    'run_specific',
    type=str,
    help='Запустить конкретный пример по имени'
)
@click.pass_context
def examples(ctx, list_examples, run_specific):
    """Запустить интерактивные примеры использования."""
    
    verbose = ctx.obj.get('verbose', False)
    debug = ctx.obj.get('debug', False)
    
    if debug:
        click.echo(f"🔍 Debug mode enabled")
        click.echo(f"🔍 Verbose mode: {verbose}")
        click.echo(f"🔍 List examples: {list_examples}")
        click.echo(f"🔍 Run specific: {run_specific}")
    
    # Находим примеры
    examples_dict = discover_examples()
    examples_dir = get_examples_directory()
    
    if debug:
        click.echo(f"🔍 Examples directory: {examples_dir}")
        click.echo(f"🔍 Found {len(examples_dict)} examples")
    
    if not examples_dict:
        click.echo("❌ Примеры не найдены", err=True)
        click.echo(f"Ожидаемая директория: {examples_dir}")
        sys.exit(1)
    
    if list_examples:
        # Показать список примеров
        if not debug:
            click.echo("📚 Доступные примеры:")
            click.echo("=" * 40)
        
        examples_table = {}
        for name, info in examples_dict.items():
            examples_table[name] = info['description']
        
        if verbose or debug:
            click.echo(format_table(examples_table, "Примеры"))
        else:
            for name, info in examples_dict.items():
                click.echo(f"• {name}: {info['description']}")
    
    elif run_specific:
        # Запустить конкретный пример
        if not debug:
            click.echo(f"🚀 Запуск примера: {run_specific}")
            click.echo("=" * 40)
        
        if run_example(run_specific):
            if not debug:
                click.echo("✅ Пример выполнен успешно")
        else:
            click.echo("❌ Ошибка выполнения примера", err=True)
            sys.exit(1)
    
    else:
        # Интерактивный режим
        if not debug:
            click.echo("🎯 Интерактивный режим примеров")
            click.echo("=" * 40)
        
        try:
            run_interactive_examples()
        except Exception as exc:
            logger.error(f"Ошибка интерактивного режима: {exc}")
            if debug:
                logger.debug("Interactive mode error details:", exc_info=True)
            click.echo(f"❌ Ошибка: {exc}", err=True)
            sys.exit(1)
