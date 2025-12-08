#!/usr/bin/env python3
"""
Интеграционный тест для прокси-провайдера.

Тестирует работу litellm-gigachat с mock-сервером прокси-провайдера.
"""

import requests
import time
import sys
import os

# Цвета для вывода
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓{RESET} {msg}")

def print_error(msg):
    print(f"{RED}✗{RESET} {msg}")

def print_info(msg):
    print(f"{BLUE}ℹ{RESET} {msg}")

def print_warning(msg):
    print(f"{YELLOW}⚠{RESET} {msg}")


class ProxyProviderTester:
    """Класс для тестирования прокси-провайдера."""
    
    def __init__(self, mock_url="http://localhost:8000", proxy_url="http://localhost:4000"):
        self.mock_url = mock_url
        self.proxy_url = proxy_url
        self.auth_header = "X-Client-Id"
        self.auth_value = "test-client-id-12345"
    
    def test_mock_server_health(self):
        """Проверка работоспособности mock-сервера."""
        print("\n" + "=" * 60)
        print("1. Проверка mock-сервера")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.mock_url}/health", timeout=5)
            if response.status_code == 200:
                print_success(f"Mock-сервер доступен: {self.mock_url}")
                return True
            else:
                print_error(f"Mock-сервер вернул код {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_error(f"Mock-сервер недоступен: {self.mock_url}")
            print_info("Запустите mock-сервер: python tests/mock_proxy_provider.py")
            return False
        except Exception as e:
            print_error(f"Ошибка подключения к mock-серверу: {e}")
            return False
    
    def test_mock_server_models(self):
        """Проверка получения списка моделей с mock-сервера."""
        print("\n" + "=" * 60)
        print("2. Проверка списка моделей mock-сервера")
        print("=" * 60)
        
        try:
            headers = {self.auth_header: self.auth_value}
            response = requests.get(f"{self.mock_url}/v1/models", headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                print_success(f"Получено {len(models)} моделей:")
                for model in models:
                    print(f"  - {model['id']}")
                return True
            else:
                print_error(f"Ошибка получения моделей: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Ошибка запроса моделей: {e}")
            return False
    
    def test_proxy_server_health(self):
        """Проверка работоспособности litellm прокси."""
        print("\n" + "=" * 60)
        print("3. Проверка litellm прокси-сервера")
        print("=" * 60)
        
        try:
            response = requests.get(f"{self.proxy_url}/health", timeout=5)
            if response.status_code == 200:
                print_success(f"Прокси-сервер доступен: {self.proxy_url}")
                return True
            else:
                print_error(f"Прокси-сервер вернул код {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print_error(f"Прокси-сервер недоступен: {self.proxy_url}")
            print_info("Запустите прокси-сервер с тестовой конфигурацией")
            return False
        except Exception as e:
            print_error(f"Ошибка подключения к прокси-серверу: {e}")
            return False
    
    def test_proxy_server_models(self):
        """Проверка получения списка моделей через прокси."""
        print("\n" + "=" * 60)
        print("4. Проверка синхронизации моделей через прокси")
        print("=" * 60)
        
        print_info("Ожидание синхронизации моделей (15 секунд)...")
        time.sleep(15)
        
        try:
            response = requests.get(f"{self.proxy_url}/v1/models", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                
                # Фильтруем модели с суффиксом -proxy
                proxy_models = [m for m in models if m.get('id', '').endswith('-proxy')]
                
                if proxy_models:
                    print_success(f"Найдено {len(proxy_models)} прокси-моделей:")
                    for model in proxy_models:
                        print(f"  - {model['id']}")
                    return True
                else:
                    print_warning("Прокси-модели не найдены")
                    print_info("Проверьте настройки MODEL_SYNC_ENABLED и PROXY_PROVIDER_ENABLED")
                    return False
            else:
                print_error(f"Ошибка получения моделей: {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Ошибка запроса моделей: {e}")
            return False
    
    def test_chat_completion(self):
        """Проверка генерации ответа через прокси."""
        print("\n" + "=" * 60)
        print("5. Проверка генерации ответа через прокси")
        print("=" * 60)
        
        try:
            # Сначала получаем список моделей
            response = requests.get(f"{self.proxy_url}/v1/models", timeout=5)
            if response.status_code != 200:
                print_error("Не удалось получить список моделей")
                return False
            
            models = response.json().get('data', [])
            proxy_models = [m for m in models if m.get('id', '').endswith('-proxy')]
            
            if not proxy_models:
                print_error("Нет доступных прокси-моделей для тестирования")
                return False
            
            # Используем первую доступную прокси-модель
            test_model = proxy_models[0]['id']
            print_info(f"Тестируем модель: {test_model}")
            
            # Отправляем запрос на генерацию
            payload = {
                "model": test_model,
                "messages": [
                    {"role": "user", "content": "Привет! Это тестовый запрос."}
                ]
            }
            
            response = requests.post(
                f"{self.proxy_url}/v1/chat/completions",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print_success("Ответ получен:")
                print(f"  {content}")
                return True
            else:
                print_error(f"Ошибка генерации: {response.status_code}")
                print(f"  {response.text}")
                return False
                
        except Exception as e:
            print_error(f"Ошибка запроса генерации: {e}")
            return False
    
    def run_all_tests(self):
        """Запуск всех тестов."""
        print("\n" + "=" * 60)
        print("🧪 ТЕСТИРОВАНИЕ ПРОКСИ-ПРОВАЙДЕРА")
        print("=" * 60)
        
        results = []
        
        # Тест 1: Mock-сервер доступен
        results.append(("Mock-сервер доступен", self.test_mock_server_health()))
        
        if not results[-1][1]:
            print_error("\n❌ Mock-сервер недоступен. Остальные тесты пропущены.")
            return False
        
        # Тест 2: Модели mock-сервера
        results.append(("Модели mock-сервера", self.test_mock_server_models()))
        
        # Тест 3: Прокси-сервер доступен
        results.append(("Прокси-сервер доступен", self.test_proxy_server_health()))
        
        if not results[-1][1]:
            print_error("\n❌ Прокси-сервер недоступен. Остальные тесты пропущены.")
            return False
        
        # Тест 4: Синхронизация моделей
        results.append(("Синхронизация моделей", self.test_proxy_server_models()))
        
        # Тест 5: Генерация ответа
        results.append(("Генерация ответа", self.test_chat_completion()))
        
        # Итоги
        print("\n" + "=" * 60)
        print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ")
        print("=" * 60)
        
        for test_name, result in results:
            if result:
                print_success(test_name)
            else:
                print_error(test_name)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        print("\n" + "=" * 60)
        if passed == total:
            print_success(f"Все тесты пройдены: {passed}/{total}")
            print("=" * 60)
            return True
        else:
            print_error(f"Пройдено тестов: {passed}/{total}")
            print("=" * 60)
            return False


if __name__ == '__main__':
    tester = ProxyProviderTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
