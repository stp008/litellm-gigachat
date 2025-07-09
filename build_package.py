#!/usr/bin/env python3
"""
Скрипт для сборки пакета litellm-gigachat для публикации в PyPI.
"""

import subprocess
import sys
import shutil
from pathlib import Path

def clean_build_dirs():
    """Очистка директорий сборки."""
    dirs_to_clean = ['build', 'dist', 'src/litellm_gigachat.egg-info']
    
    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"Удаление {dir_path}")
            shutil.rmtree(dir_path)

def install_build_tools():
    """Установка инструментов для сборки."""
    print("Установка инструментов сборки...")
    subprocess.run([
        sys.executable, "-m", "pip", "install", "--upgrade",
        "build", "twine", "setuptools", "wheel"
    ], check=True)

def build_package():
    """Сборка пакета."""
    print("Сборка пакета...")
    subprocess.run([
        sys.executable, "-m", "build"
    ], check=True)

def check_package():
    """Проверка собранного пакета."""
    print("Проверка пакета...")
    subprocess.run([
        sys.executable, "-m", "twine", "check", "dist/*"
    ], check=True)

def main():
    """Основная функция сборки."""
    print("🔨 Сборка пакета litellm-gigachat")
    print("=" * 50)
    
    try:
        clean_build_dirs()
        install_build_tools()
        build_package()
        check_package()
        
        print("\n✅ Пакет успешно собран!")
        print("📦 Файлы пакета находятся в директории dist/")
        print("\nДля публикации в PyPI выполните:")
        print("  python publish_package.py")
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при сборке: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
