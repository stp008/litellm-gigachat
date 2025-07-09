#!/usr/bin/env python3
"""
Скрипт для публикации пакета litellm-gigachat в PyPI.
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dist_files():
    """Проверка наличия файлов для публикации."""
    dist_dir = Path("dist")
    if not dist_dir.exists():
        print("❌ Директория dist/ не найдена. Сначала выполните сборку:")
        print("  python build_package.py")
        return False
    
    files = list(dist_dir.glob("*"))
    if not files:
        print("❌ В директории dist/ нет файлов для публикации.")
        return False
    
    print("📦 Найдены файлы для публикации:")
    for file in files:
        print(f"  - {file.name}")
    
    return True

def publish_to_test_pypi():
    """Публикация в Test PyPI."""
    print("\n🧪 Публикация в Test PyPI...")
    print("Для публикации в Test PyPI нужен API токен.")
    print("Получить токен можно на: https://test.pypi.org/manage/account/token/")
    
    confirm = input("\nПродолжить публикацию в Test PyPI? (y/N): ")
    if confirm.lower() != 'y':
        print("Публикация отменена.")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "twine", "upload",
            "--repository", "testpypi",
            "dist/*"
        ], check=True)
        
        print("\n✅ Пакет успешно опубликован в Test PyPI!")
        print("🔗 Проверить: https://test.pypi.org/project/litellm-gigachat/")
        print("\nДля установки из Test PyPI:")
        print("  pip install --index-url https://test.pypi.org/simple/ litellm-gigachat")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при публикации в Test PyPI: {e}")
        return False

def publish_to_pypi():
    """Публикация в основной PyPI."""
    print("\n🚀 Публикация в основной PyPI...")
    print("⚠️  ВНИМАНИЕ: Это публикация в основной PyPI!")
    print("После публикации версию нельзя будет изменить или удалить.")
    print("Для публикации нужен API токен от https://pypi.org/manage/account/token/")
    
    confirm = input("\nВы уверены, что хотите опубликовать в основной PyPI? (y/N): ")
    if confirm.lower() != 'y':
        print("Публикация отменена.")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "twine", "upload",
            "dist/*"
        ], check=True)
        
        print("\n🎉 Пакет успешно опубликован в PyPI!")
        print("🔗 Проверить: https://pypi.org/project/litellm-gigachat/")
        print("\nДля установки:")
        print("  pip install litellm-gigachat")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Ошибка при публикации в PyPI: {e}")
        return False

def main():
    """Основная функция публикации."""
    print("📤 Публикация пакета litellm-gigachat")
    print("=" * 50)
    
    if not check_dist_files():
        sys.exit(1)
    
    print("\nВыберите репозиторий для публикации:")
    print("1. Test PyPI (рекомендуется для тестирования)")
    print("2. Основной PyPI (финальная публикация)")
    print("3. Отмена")
    
    choice = input("\nВаш выбор (1-3): ")
    
    if choice == "1":
        if publish_to_test_pypi():
            print("\n💡 После тестирования в Test PyPI можно опубликовать в основной PyPI.")
    elif choice == "2":
        if publish_to_pypi():
            print("\n🎊 Поздравляем с успешной публикацией!")
    else:
        print("Публикация отменена.")

if __name__ == "__main__":
    main()
