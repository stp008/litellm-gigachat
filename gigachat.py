#!/usr/bin/env python3
"""
Точка входа для тестирования основной функциональности GigaChat.
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.gigachat_client import main

if __name__ == "__main__":
    main()
