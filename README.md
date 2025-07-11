# Интеграция GigaChat с LiteLLM

[![GitHub stars](https://img.shields.io/github/stars/stp008/litellm-gigachat?style=social)](https://github.com/stp008/litellm-gigachat/stargazers)
[![PyPI version](https://img.shields.io/pypi/v/litellm-gigachat.svg)](https://pypi.org/project/litellm-gigachat/)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.65.1-green.svg)](https://github.com/BerriAI/litellm)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GigaChat](https://img.shields.io/badge/GigaChat-API-red.svg)](https://developers.sber.ru/portal/products/gigachat-api)

**Полнофункциональная интеграция GigaChat API с LiteLLM** - готовое решение для подключения российской языковой модели GigaChat через стандартный OpenAI-совместимый интерфейс. Включает автоматическое обновление токенов, преобразование контента и полную совместимость с AI-ассистентом Cline.

## 📚 Документация

**[Полная документация](docs/README.md)** | **[CLI команды](docs/CLI_FEATURES.md)** | **[FAQ](docs/FAQ.md)** | **[Тестовые запросы](docs/TEST_REQUESTS.md)** | **[Причины несовместимости с OpenAI API](docs/GIGACHAT_COMPATIBILITY.md)**

## 🚀 Основные возможности

-  **Автоматическое обновление токенов**
-  **Автоматическая настройка сертификатов**
-  **Совместимость с Cline** 
-  **Streaming поддержка**

## 📦 Установка

### Через pip (рекомендуется)

```bash
# Установка пакета
pip install litellm-gigachat

# Проверка установки
litellm-gigachat --version
```

### Из исходников (для разработки)

```bash
# 1. Клонирование репозитория
git clone https://github.com/stp008/litellm-gigachat.git
cd litellm-gigachat

# 2. Установка в режиме разработки
pip install -e .

# 3. Проверка установки
litellm-gigachat --version
```

## 🎯 Быстрый старт

### 1. Настройка API ключа

```bash
# Установите ваш authorization key от GigaChat
export GIGACHAT_AUTH_KEY="ваш_authorization_key"
```

### 2. Запуск прокси-сервера

```bash
# Через установленный пакет (рекомендуется)
litellm-gigachat

# Через исходники (для разработки)
python tools/start_proxy.py

# С кастомными параметрами (только для установленного пакета)
litellm-gigachat --host 127.0.0.1 --port 8000

# С кастомным файлом конфигурации
litellm-gigachat --config my_config.yml

# Справка по командам
litellm-gigachat --help
```

**Примечание:** Если вы работаете с исходниками проекта (клонировали репозиторий), используйте `python tools/start_proxy.py`. Если установили пакет через pip, используйте команду `litellm-gigachat`.

### 3. Использование через OpenAI API

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="any-key"  # Токен управляется автоматически
)

response = client.chat.completions.create(
    model="gigachat",
    messages=[{"role": "user", "content": "Привет, GigaChat!"}]
)

print(response.choices[0].message.content)
```

### 4. Использование через LiteLLM (программно)

```python
import litellm_gigachat

# Автоматическая настройка интеграции
litellm_gigachat.setup_litellm_gigachat_integration()

# Использование через LiteLLM
import litellm

response = litellm.completion(
    model="openai/GigaChat",
    api_base="https://gigachat.devices.sberbank.ru/api/v1",
    api_key=litellm_gigachat.get_gigachat_token(),
    messages=[{"role": "user", "content": "Привет!"}]
)

print(response.choices[0].message.content)
```

### Использование через Cline

Допустимо использовать сервер как в качестве OpenAI совместимого провайдера, так и в качестве LiteLLM провайдера. В случае использования второго варианта появляется больше доступных опций.

##### Настройка LiteLLM провайдера (рекомендуется):
<img src="docs/images/cline-settings-litellm.png" alt="Настройки Cline через LiteLLM" width="500">

##### Настройки OpenAI Compatible провайдера:
<img src="docs/images/cline-settings-openai.png" alt="Настройки Cline с OpenAI совместимостью" width="500">

В настройках Cline укажите следующие параметры:

**Основные настройки:**
1. **API Provider**: Выберите `LiteLLM` или `OpenAI Compatible` из выпадающего списка
2. **Base URL**: Введите `http://localhost:4000` (без слэша в конце)
3. **API Key**: Введите любое значение, например `gigachat-key` (токен управляется автоматически)
4. **Model**: Выберите одну из моделей:
   - `gigachat` - основная модель (рекомендуется для начала)
   - `gigachat-pro` - продвинутая модель для сложных задач
   - `gigachat-max` - модель с максимальными возможностями

#### 4.3 Дополнительные настройки (опционально)

- **Temperature**: 0.7 (для баланса между креативностью и точностью)
- **Max Tokens**: 4000 (максимальная длина ответа)
- **Timeout**: 60 секунд


### Тестирование интеграции с Cline

```bash
python test_cline_integration.py
```

## 🔧 CLI команды

После установки пакета доступна команда `litellm-gigachat` с полным набором команд для управления прокси-сервером:

### 🌐 Глобальные опции

Доступны для всех команд:

| Опция | Описание |
|-------|----------|
| `--version` | Показать версию и выйти |
| `-v, --verbose` | Включить подробный вывод |
| `-d, --debug` | Включить режим отладки |
| `--help` | Показать справку |

### 📚 Основные команды

#### 1. `start` - Запуск прокси-сервера

Запускает LiteLLM прокси-сервер для GigaChat API.

```bash
litellm-gigachat start [OPTIONS]
```

**Опции:**
- `--host TEXT` - Хост сервера [default: 0.0.0.0]
- `--port INTEGER` - Порт сервера [default: 4000]
- `--config TEXT` - Файл конфигурации [default: config.yml]

**Примеры:**
```bash
# Запуск с настройками по умолчанию
litellm-gigachat start

# Запуск на localhost:8080
litellm-gigachat start --host localhost --port 8080

# Запуск с кастомным конфигом
litellm-gigachat start --config my-config.yml

# Запуск в verbose режиме
litellm-gigachat --verbose start
```

#### 2. `test` - Тестирование подключения

Выполняет комплексное тестирование подключения к GigaChat API.

```bash
litellm-gigachat test [OPTIONS]
```

**Опции:**
- `--timeout INTEGER` - Таймаут тестирования в секундах [default: 30]

**Выполняемые тесты:**
- Проверка переменных окружения
- Тестирование TokenManager
- Проверка GigaChat API
- Тестирование LiteLLM интеграции

**Примеры:**
```bash
# Базовое тестирование
litellm-gigachat test

# Тестирование с увеличенным таймаутом
litellm-gigachat test --timeout 60

# Подробное тестирование
litellm-gigachat --verbose test
```

#### 3. `token-info` - Информация о токене

Показывает детальную информацию о текущем токене доступа.

```bash
litellm-gigachat token-info [OPTIONS]
```

**Опции:**
- `--format [json|table]` - Формат вывода [default: table]

**Отображаемая информация:**
- Статус токена (активен/неактивен/истек)
- Время истечения и оставшееся время
- Область действия (scope)
- Переменные окружения (в verbose режиме)

**Примеры:**
```bash
# Показать информацию о токене
litellm-gigachat token-info

# Вывод в JSON формате
litellm-gigachat token-info --format json

# Подробная информация
litellm-gigachat --verbose token-info
```

#### 4. `refresh-token` - Обновление токена

Принудительно обновляет токен доступа.

```bash
litellm-gigachat refresh-token [OPTIONS]
```

**Опции:**
- `--force` - Принудительно обновить токен даже если текущий еще действителен

**Логика работы:**
- Проверяет текущий токен
- Обновляет только если осталось < 5 минут (без --force)
- С --force обновляет принудительно

**Примеры:**
```bash
# Обновить токен если нужно
litellm-gigachat refresh-token

# Принудительно обновить токен
litellm-gigachat refresh-token --force

# Подробное обновление
litellm-gigachat --verbose refresh-token --force
```

#### 5. `examples` - Интерактивные примеры

Запускает примеры использования из директории examples/.

```bash
litellm-gigachat examples [OPTIONS]
```

**Опции:**
- `--list` - Показать список доступных примеров
- `--run TEXT` - Запустить конкретный пример по имени

**Режимы работы:**
- Интерактивный выбор (по умолчанию)
- Список примеров (--list)
- Запуск конкретного примера (--run)

**Примеры:**
```bash
# Интерактивный режим выбора примеров
litellm-gigachat examples

# Показать список примеров
litellm-gigachat examples --list

# Запустить конкретный пример
litellm-gigachat examples --run basic_usage

# Подробный список примеров
litellm-gigachat --verbose examples --list
```

#### 6. `version` - Информация о версии

Показывает версию пакета и компонентов системы.

```bash
litellm-gigachat version [OPTIONS]
```

**Опции:**
- `--components` - Показать версии всех компонентов
- `--json-output` - Вывод в формате JSON
- `--check-updates` - Проверить доступность обновлений

**Отображаемая информация:**
- Версия пакета litellm-gigachat
- Версии зависимостей (litellm, requests, etc.)
- Системная информация (Python, платформа)
- Информация об окружении

**Примеры:**
```bash
# Базовая информация о версии
litellm-gigachat version

# Показать все компоненты
litellm-gigachat version --components

# JSON вывод
litellm-gigachat version --json-output

# Проверить обновления
litellm-gigachat version --check-updates

# Полная информация в verbose режиме
litellm-gigachat --verbose version
```

### 🔧 Режимы работы

#### Обычный режим
- Минимальный вывод
- Только основные сообщения
- Подходит для автоматизации

#### Verbose режим (`-v, --verbose`)
- Дополнительная информация
- Расширенные таблицы
- Подробные логи операций

#### Debug режим (`-d, --debug`)
- Максимально подробный вывод
- Отладочная информация
- Трассировка ошибок
- Технические детали

### 🚀 Примеры комбинированного использования

```bash
# Полная диагностика в debug режиме
litellm-gigachat --debug test --timeout 60

# Запуск сервера с отладкой
litellm-gigachat --debug start --host localhost --port 8080

# Получение полной информации о системе
litellm-gigachat --verbose version --components --check-updates

# Принудительное обновление токена с подробным выводом
litellm-gigachat --verbose refresh-token --force

# Запуск примера с отладкой
litellm-gigachat --debug examples --run internal_gigachat_example
```

### 🌍 Переменные окружения

CLI автоматически загружает переменные из `.env` файла:

- `GIGACHAT_AUTH_KEY` - **Обязательная** переменная с ключом авторизации
- `GIGACHAT_BASE_URL` - URL базы GigaChat API (опционально)
- `GIGACHAT_SCOPE` - Область действия токена (опционально)
- `GIGACHAT_VERIFY_SSL_CERTS` - Проверка SSL сертификатов (опционально)

### 📋 Быстрая справка

```bash
# Показать все доступные команды
litellm-gigachat --help

# Справка по конкретной команде
litellm-gigachat start --help
litellm-gigachat test --help
litellm-gigachat token-info --help

# Проверить версию
litellm-gigachat --version

# Быстрый старт
export GIGACHAT_AUTH_KEY="ваш_ключ"
litellm-gigachat start
```

## 📊 Доступные модели

### Официальные модели (с токенами)
| Модель API | Описание |
|------------|----------|
| `gigachat` | Основная модель для общих задач |
| `gigachat-pro` | Продвинутая модель для сложных задач |
| `gigachat-max` | Модель с максимальными возможностями |

### Внутренние модели (с заголовками)
| Модель API | Описание |
|------------|----------|
| `gigachat-internal` | Внутренняя установка основной модели |
| `gigachat-pro-internal` | Внутренняя установка продвинутой модели |
| `gigachat-max-internal` | Внутренняя установка модели с максимальными возможностями |

**Примечание:** Внутренние модели доступны только при настройке переменных окружения для внутренней установки (см. раздел "Настройка внутренней установки").

## 🏢 Настройка внутренней установки GigaChat

Пакет поддерживает работу с внутренними установками GigaChat, которые используют заголовки аутентификации вместо токенов.

### Переменные окружения

```bash
# Включить поддержку внутренней установки
export GIGACHAT_INTERNAL_ENABLED=true

# URL внутренней установки (обязательно)
export GIGACHAT_INTERNAL_URL=https://my-gigachat.company.com/api/v1

# Название заголовка аутентификации (по умолчанию: X-Client-Id)
export GIGACHAT_AUTH_HEADER_NAME=X-Client-Id

# Значение заголовка аутентификации (обязательно)
export GIGACHAT_AUTH_HEADER_VALUE=bddcba1a-6139-4b5f-9994-90f1b74e9109
```

### Использование внутренних моделей

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="any-key"  # Заголовки управляются автоматически
)

# Использование внутренней модели
response = client.chat.completions.create(
    model="gigachat-internal",  # Автоматически добавится заголовок X-Client-Id
    messages=[{"role": "user", "content": "Привет!"}]
)

print(response.choices[0].message.content)
```

### Тестирование внутренней установки

```bash
# Запуск примера
python examples/internal_gigachat_example.py

# Запуск тестов
python tests/test_internal_gigachat.py

# Тестирование через curl
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{
    "model": "gigachat-internal",
    "messages": [{"role": "user", "content": "Привет!"}]
  }'
```

### Кастомизация

Вы можете настроить любые параметры:

```bash
# Пример для другой установки
export GIGACHAT_INTERNAL_ENABLED=true
export GIGACHAT_INTERNAL_URL=https://internal-ai.company.ru/v2
export GIGACHAT_AUTH_HEADER_NAME=Authorization-Key
export GIGACHAT_AUTH_HEADER_VALUE=secret-key-123
```

## 🧪 Тестирование

### После установки через pip

```bash
# Проверка версии и CLI
litellm-gigachat --version
litellm-gigachat --help

# Запуск прокси-сервера (требует GIGACHAT_AUTH_KEY)
export GIGACHAT_AUTH_KEY="ваш_ключ"
litellm-gigachat

# Тестирование через curl (в другом терминале)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{
    "model": "gigachat",
    "messages": [{"role": "user", "content": "Привет!"}]
  }'
```

### При разработке из исходников

```bash
# Базовая функциональность
python tests/test_basic_functionality.py

# Интеграция с Cline
python tests/test_cline_integration.py

# Интерактивные примеры
python examples/basic_usage.py

# Все тесты
python -m pytest tests/
```

### Быстрая проверка работоспособности

```python
# test_quick.py
import openai

client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="test-key"
)

try:
    response = client.chat.completions.create(
        model="gigachat",
        messages=[{"role": "user", "content": "Тест"}]
    )
    print("✅ Интеграция работает!")
    print(f"Ответ: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ Ошибка: {e}")
```

## 🚨 Устранение неполадок

### Ошибка "Authorization key не найден"
```bash
# Установите переменную окружения
export GIGACHAT_AUTH_KEY="ваш_ключ"

# Проверьте, что ключ установлен
echo $GIGACHAT_AUTH_KEY
```

### Проблемы с CLI командой
```bash
# Проверьте, что пакет установлен
pip list | grep litellm-gigachat

# Переустановите пакет при необходимости
pip install --upgrade litellm-gigachat

# Проверьте версию
litellm-gigachat --version
```

### Проблемы с прокси-сервером
```bash
# Убедитесь, что прокси запущен
litellm-gigachat

# Проверьте, что порт свободен
lsof -i :4000

# Запустите на другом порту
litellm-gigachat --port 8000
```

### Проблемы с Cline
- Убедитесь, что прокси запущен: `litellm-gigachat`
- Проверьте URL: `http://localhost:4000`
- Проверьте, что порт доступен: `curl http://localhost:4000/health`
- Тест интеграции: `python tests/test_cline_integration.py`

### Проблемы с сертификатами
```bash
# Проверьте подключение к GigaChat API
curl -k https://gigachat.devices.sberbank.ru/api/v1/models

# При проблемах с SSL попробуйте переустановить certifi
pip install --upgrade certifi
```

Полное руководство: **[❓ FAQ](docs/FAQ.md)**

## 🔗 Полезные ссылки

- **[📚 Полная документация](docs/README.md)** - подробное руководство
- **[❓ FAQ](docs/FAQ.md)** - часто задаваемые вопросы
- **[🔧 API Reference](docs/TEST_REQUESTS.md)** - примеры запросов

---

**Лицензия**: MIT | **Поддерживаемые версии**: Python 3.8+
