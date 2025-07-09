#!/usr/bin/env python3
"""
Точка входа для запуска прокси-сервера с новой структурой проекта.
"""

import sys
import os

# Добавляем корневую директорию в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.litellm_gigachat.proxy import main

if __name__ == "__main__":
    main()
