#!/usr/bin/env python3
"""
Точка входа для запуска примеров использования.
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from examples.basic_usage import main

if __name__ == "__main__":
    main()
