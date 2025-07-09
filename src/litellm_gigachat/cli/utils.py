"""
Утилиты для CLI модуля.
"""

import logging
import os
import sys
from datetime import datetime
from importlib import metadata
from pathlib import Path


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Настройка логирования в зависимости от режима."""
    
    if debug:
        level = logging.DEBUG
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
        
        # В режиме отладки также сохраняем логи в файл
        log_file = f"litellm-gigachat-debug-{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(log_file, encoding='utf-8')
            ]
        )
        
        logger = logging.getLogger(__name__)
        logger.debug(f"Debug mode enabled. Logs saved to: {log_file}")
        
    elif verbose:
        level = logging.INFO
        format_str = "%(asctime)s - %(levelname)s - %(message)s"
        
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[logging.StreamHandler(sys.stdout)]
        )
        
    else:
        # Обычный режим - минимальный вывод
        level = logging.WARNING
        format_str = "%(message)s"
        
        logging.basicConfig(
            level=level,
            format=format_str,
            handlers=[logging.StreamHandler(sys.stdout)]
        )


def get_package_version() -> str:
    """Получить версию пакета."""
    try:
        return metadata.version("litellm-gigachat")
    except metadata.PackageNotFoundError:
        return "unknown"


def get_component_versions() -> dict:
    """Получить версии всех компонентов."""
    components = {}
    
    # Основные зависимости
    dependencies = [
        "litellm-gigachat",
        "litellm", 
        "requests",
        "certifi",
        "python-dotenv",
        "click"
    ]
    
    for dep in dependencies:
        try:
            components[dep] = metadata.version(dep)
        except metadata.PackageNotFoundError:
            components[dep] = "not installed"
    
    # Версия Python
    components["python"] = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    
    return components


def check_environment_variables() -> dict:
    """Проверить переменные окружения."""
    env_vars = {
        "GIGACHAT_AUTH_KEY": os.getenv("GIGACHAT_AUTH_KEY"),
        "GIGACHAT_BASE_URL": os.getenv("GIGACHAT_BASE_URL"),
        "GIGACHAT_SCOPE": os.getenv("GIGACHAT_SCOPE"),
    }
    
    return {k: "✓ set" if v else "✗ not set" for k, v in env_vars.items()}


def find_config_file(config_path: str) -> Path:
    """Найти файл конфигурации."""
    config = Path(config_path)
    
    # Если путь абсолютный, используем его
    if config.is_absolute():
        return config
    
    # Ищем относительно текущей директории
    if config.exists():
        return config.resolve()
    
    # Ищем в родительской директории
    parent_config = Path("..") / config
    if parent_config.exists():
        return parent_config.resolve()
    
    # Ищем в корне проекта
    project_root = Path(__file__).parent.parent.parent.parent
    root_config = project_root / config
    if root_config.exists():
        return root_config.resolve()
    
    # Возвращаем исходный путь, даже если файл не существует
    return config.resolve()


def format_table(data: dict, title: str = None) -> str:
    """Форматировать данные в виде таблицы."""
    if not data:
        return "No data to display"
    
    # Вычисляем максимальную ширину колонок
    max_key_len = max(len(str(k)) for k in data.keys())
    max_val_len = max(len(str(v)) for v in data.values())
    
    # Минимальная ширина
    max_key_len = max(max_key_len, 10)
    max_val_len = max(max_val_len, 10)
    
    # Создаем разделитель
    separator = "+" + "-" * (max_key_len + 2) + "+" + "-" * (max_val_len + 2) + "+"
    
    lines = []
    
    if title:
        lines.append(f"\n{title}")
        lines.append("=" * len(title))
    
    lines.append(separator)
    lines.append(f"| {'Key':<{max_key_len}} | {'Value':<{max_val_len}} |")
    lines.append(separator)
    
    for key, value in data.items():
        lines.append(f"| {str(key):<{max_key_len}} | {str(value):<{max_val_len}} |")
    
    lines.append(separator)
    
    return "\n".join(lines)


def validate_port(port: int) -> bool:
    """Проверить корректность порта."""
    return 1 <= port <= 65535


def validate_host(host: str) -> bool:
    """Проверить корректность хоста."""
    if not host:
        return False
    
    # Простая проверка
    if host in ["localhost", "0.0.0.0"]:
        return True
    
    # Проверка IP адреса (упрощенная)
    parts = host.split(".")
    if len(parts) == 4:
        try:
            return all(0 <= int(part) <= 255 for part in parts)
        except ValueError:
            return False
    
    # Проверка доменного имени (упрощенная)
    return all(c.isalnum() or c in ".-" for c in host)
