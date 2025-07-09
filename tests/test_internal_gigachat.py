#!/usr/bin/env python3
"""
Тесты для внутренней установки GigaChat
"""

import os
import unittest
from unittest.mock import patch, MagicMock
import sys
import tempfile

# Добавляем путь к модулю
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from litellm_gigachat.core.internal_header_manager import (
    InternalHeaderManager,
    get_global_internal_header_manager,
    get_internal_auth_headers,
    is_internal_gigachat_enabled
)
from litellm_gigachat.callbacks.internal_header_callback import (
    InternalHeaderCallback,
    get_internal_header_callback
)


class TestInternalHeaderManager(unittest.TestCase):
    """Тесты для InternalHeaderManager"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Сохраняем оригинальные переменные окружения
        self.original_env = {}
        env_vars = [
            'GIGACHAT_INTERNAL_ENABLED',
            'GIGACHAT_INTERNAL_URL',
            'GIGACHAT_AUTH_HEADER_NAME',
            'GIGACHAT_AUTH_HEADER_VALUE',
            'GIGACHAT_INTERNAL_MODEL_SUFFIX'
        ]
        
        for var in env_vars:
            self.original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
    
    def tearDown(self):
        """Очистка после каждого теста"""
        # Восстанавливаем оригинальные переменные окружения
        for var, value in self.original_env.items():
            if value is not None:
                os.environ[var] = value
            elif var in os.environ:
                del os.environ[var]
    
    def test_disabled_by_default(self):
        """Тест: внутренняя установка отключена по умолчанию"""
        manager = InternalHeaderManager()
        
        self.assertFalse(manager.is_enabled())
        self.assertEqual(manager.get_auth_headers(), {})
        self.assertIsNone(manager.get_internal_url())
        self.assertEqual(manager.get_model_names(), [])
    
    def test_enabled_configuration(self):
        """Тест: корректная конфигурация при включенной внутренней установке"""
        os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
        os.environ['GIGACHAT_INTERNAL_URL'] = 'https://test.example.com/api/v1'
        os.environ['GIGACHAT_AUTH_HEADER_NAME'] = 'X-Test-Header'
        os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'test-value-123'
        os.environ['GIGACHAT_INTERNAL_MODEL_SUFFIX'] = 'test'
        
        manager = InternalHeaderManager()
        
        self.assertTrue(manager.is_enabled())
        self.assertEqual(manager.get_internal_url(), 'https://test.example.com/api/v1')
        self.assertEqual(manager.get_auth_headers(), {'X-Test-Header': 'test-value-123'})
        self.assertEqual(manager.model_suffix, 'test')
        
        expected_models = ['gigachat-test', 'gigachat-pro-test', 'gigachat-max-test']
        self.assertEqual(manager.get_model_names(), expected_models)
    
    def test_is_internal_model(self):
        """Тест: проверка определения внутренних моделей"""
        os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
        os.environ['GIGACHAT_INTERNAL_MODEL_SUFFIX'] = 'custom'
        
        manager = InternalHeaderManager()
        
        # Внутренние модели
        self.assertTrue(manager.is_internal_model('gigachat-custom'))
        self.assertTrue(manager.is_internal_model('gigachat-pro-custom'))
        self.assertTrue(manager.is_internal_model('gigachat-max-custom'))
        
        # Обычные модели
        self.assertFalse(manager.is_internal_model('gigachat'))
        self.assertFalse(manager.is_internal_model('gigachat-pro'))
        self.assertFalse(manager.is_internal_model('gigachat-internal'))
    
    def test_validation(self):
        """Тест: валидация конфигурации"""
        # Отключенная установка всегда валидна
        manager = InternalHeaderManager()
        self.assertTrue(manager.validate_configuration())
        
        # Включенная установка без URL
        os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
        manager = InternalHeaderManager()
        self.assertFalse(manager.validate_configuration())
        
        # Включенная установка без заголовка
        os.environ['GIGACHAT_INTERNAL_URL'] = 'https://test.example.com'
        manager = InternalHeaderManager()
        self.assertFalse(manager.validate_configuration())
        
        # Полная корректная конфигурация
        os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'test-value'
        manager = InternalHeaderManager()
        self.assertTrue(manager.validate_configuration())
    
    def test_default_values(self):
        """Тест: значения по умолчанию"""
        os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
        os.environ['GIGACHAT_INTERNAL_URL'] = 'https://test.example.com'
        os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'test-value'
        
        manager = InternalHeaderManager()
        
        # Значения по умолчанию
        self.assertEqual(manager.header_name, 'X-Client-Id')
        self.assertEqual(manager.model_suffix, 'internal')
    
    def test_configuration_info(self):
        """Тест: получение информации о конфигурации"""
        os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
        os.environ['GIGACHAT_INTERNAL_URL'] = 'https://test.example.com'
        os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'test-value'
        
        manager = InternalHeaderManager()
        config_info = manager.get_configuration_info()
        
        self.assertIsInstance(config_info, dict)
        self.assertTrue(config_info['enabled'])
        self.assertTrue(config_info['has_header_value'])
        self.assertTrue(config_info['is_valid'])
        self.assertIn('gigachat-internal', config_info['available_models'])


class TestInternalHeaderCallback(unittest.TestCase):
    """Тесты для InternalHeaderCallback"""
    
    def setUp(self):
        """Настройка перед каждым тестом"""
        # Настраиваем тестовое окружение
        os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
        os.environ['GIGACHAT_INTERNAL_URL'] = 'https://test-internal.example.com/api/v1'
        os.environ['GIGACHAT_AUTH_HEADER_NAME'] = 'X-Test-Auth'
        os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'test-auth-value'
        os.environ['GIGACHAT_INTERNAL_MODEL_SUFFIX'] = 'test'
        
        self.callback = InternalHeaderCallback()
    
    def tearDown(self):
        """Очистка после теста"""
        env_vars = [
            'GIGACHAT_INTERNAL_ENABLED',
            'GIGACHAT_INTERNAL_URL',
            'GIGACHAT_AUTH_HEADER_NAME',
            'GIGACHAT_AUTH_HEADER_VALUE',
            'GIGACHAT_INTERNAL_MODEL_SUFFIX'
        ]
        
        for var in env_vars:
            if var in os.environ:
                del os.environ[var]
    
    def test_is_internal_gigachat_model(self):
        """Тест: определение внутренних моделей"""
        # Импортируем модули заново, чтобы обновить глобальные переменные
        import importlib
        import sys
        
        # Перезагружаем модули
        if 'litellm_gigachat.core.internal_header_manager' in sys.modules:
            importlib.reload(sys.modules['litellm_gigachat.core.internal_header_manager'])
        if 'litellm_gigachat.callbacks.internal_header_callback' in sys.modules:
            importlib.reload(sys.modules['litellm_gigachat.callbacks.internal_header_callback'])
        
        # Импортируем заново
        from litellm_gigachat.callbacks.internal_header_callback import InternalHeaderCallback
        
        # Создаем новый callback
        callback = InternalHeaderCallback()
        
        # Внутренние модели (используем суффикс 'test' из setUp)
        self.assertTrue(callback._is_internal_gigachat_model('gigachat-test', {}))
        self.assertTrue(callback._is_internal_gigachat_model('gigachat-pro-test', {}))
        
        # Обычные модели
        self.assertFalse(callback._is_internal_gigachat_model('gigachat', {}))
        self.assertFalse(callback._is_internal_gigachat_model('gpt-4', {}))
        self.assertFalse(callback._is_internal_gigachat_model('gigachat-internal', {}))  # Другой суффикс
        
        # Проверка по URL
        data_with_internal_url = {
            'api_base': 'https://test-internal.example.com/api/v1'
        }
        self.assertTrue(callback._is_internal_gigachat_model('some-model', data_with_internal_url))
    
    @patch('litellm_gigachat.callbacks.internal_header_callback.logger')
    async def test_async_pre_call_hook_internal_model(self, mock_logger):
        """Тест: обработка внутренней модели в pre_call_hook"""
        # Подготавливаем данные запроса
        data = {
            'model': 'gigachat-test',
            'litellm_params': {
                'api_base': 'https://original.example.com',
                'api_key': 'original-key'
            }
        }
        
        # Мокаем зависимости
        user_api_key_dict = MagicMock()
        cache = MagicMock()
        
        # Вызываем hook
        result = await self.callback.async_pre_call_hook(
            user_api_key_dict, cache, data, "completion"
        )
        
        # Проверяем результат
        self.assertEqual(result['litellm_params']['api_base'], 'https://test-internal.example.com/api/v1')
        self.assertEqual(result['litellm_params']['api_key'], 'none')
        self.assertIn('extra_headers', result['litellm_params'])
        self.assertEqual(result['litellm_params']['extra_headers']['X-Test-Auth'], 'test-auth-value')
    
    @patch('litellm_gigachat.callbacks.internal_header_callback.logger')
    async def test_async_pre_call_hook_regular_model(self, mock_logger):
        """Тест: обработка обычной модели в pre_call_hook"""
        # Подготавливаем данные запроса
        original_data = {
            'model': 'gigachat',
            'litellm_params': {
                'api_base': 'https://gigachat.devices.sberbank.ru/api/v1',
                'api_key': 'original-key'
            }
        }
        
        # Мокаем зависимости
        user_api_key_dict = MagicMock()
        cache = MagicMock()
        
        # Вызываем hook
        result = await self.callback.async_pre_call_hook(
            user_api_key_dict, cache, original_data, "completion"
        )
        
        # Проверяем, что данные не изменились
        self.assertEqual(result['litellm_params']['api_base'], 'https://gigachat.devices.sberbank.ru/api/v1')
        self.assertEqual(result['litellm_params']['api_key'], 'original-key')
        self.assertNotIn('extra_headers', result['litellm_params'])


class TestGlobalFunctions(unittest.TestCase):
    """Тесты для глобальных функций"""
    
    def test_global_functions(self):
        """Тест: глобальные функции работают корректно"""
        # Сохраняем текущие переменные окружения
        original_env = {}
        env_vars = [
            'GIGACHAT_INTERNAL_ENABLED',
            'GIGACHAT_AUTH_HEADER_NAME',
            'GIGACHAT_AUTH_HEADER_VALUE'
        ]
        
        for var in env_vars:
            original_env[var] = os.environ.get(var)
            if var in os.environ:
                del os.environ[var]
        
        try:
            # Тестируем новый менеджер без настройки окружения
            manager_disabled = InternalHeaderManager()
            self.assertFalse(manager_disabled.is_enabled())
            self.assertEqual(manager_disabled.get_auth_headers(), {})
            
            # Настраиваем окружение
            os.environ['GIGACHAT_INTERNAL_ENABLED'] = 'true'
            os.environ['GIGACHAT_AUTH_HEADER_NAME'] = 'X-Test'
            os.environ['GIGACHAT_AUTH_HEADER_VALUE'] = 'test-value'
            
            # Создаем новый менеджер для обновления настроек
            manager_enabled = InternalHeaderManager()
            
            # Проверяем функции с настроенным окружением
            self.assertTrue(manager_enabled.is_enabled())
            self.assertEqual(manager_enabled.get_auth_headers(), {'X-Test': 'test-value'})
            
        finally:
            # Восстанавливаем оригинальные переменные окружения
            for var, value in original_env.items():
                if value is not None:
                    os.environ[var] = value
                elif var in os.environ:
                    del os.environ[var]


def run_tests():
    """Запуск всех тестов"""
    print("🧪 Запуск тестов внутренней установки GigaChat...")
    print("=" * 60)
    
    # Создаем test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Добавляем тесты
    suite.addTests(loader.loadTestsFromTestCase(TestInternalHeaderManager))
    suite.addTests(loader.loadTestsFromTestCase(TestInternalHeaderCallback))
    suite.addTests(loader.loadTestsFromTestCase(TestGlobalFunctions))
    
    # Запускаем тесты
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Выводим результат
    print("\n" + "=" * 60)
    if result.wasSuccessful():
        print("✅ Все тесты пройдены успешно!")
    else:
        print(f"❌ Тесты завершились с ошибками:")
        print(f"   Неудачных тестов: {len(result.failures)}")
        print(f"   Ошибок: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
