# LiteLLM GigaChat Integration

Полнофункциональная интеграция GigaChat API с LiteLLM, включающая автоматическое обновление токенов, преобразование контента и совместимость с Cline.

## 🚀 Основные возможности

- ✅ **Автоматическое обновление токенов** - токены обновляются каждые 30 минут автоматически
- ✅ **Множественные модели** - поддержка GigaChat, GigaChat-Pro, GigaChat-Max
- ✅ **Автоматическая настройка сертификатов** - российские корневые сертификаты устанавливаются автоматически
- ✅ **Совместимость с Cline** - полная поддержка AI-ассистента Cline без ошибок "invalid JSON syntax"

## 📦 Установка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Получение Authorization Key

1. Откройте [личный кабинет GigaChat](https://developers.sber.ru/studio/workspaces)
2. Перейдите в проект GigaChat API
3. Откройте "Настройки API"
4. Нажмите "Получить ключ"
5. Скопируйте Authorization Key

### 3. Настройка переменной окружения

```bash
export GIGACHAT_AUTH_KEY="ваш_authorization_key_в_base64"
```

Или создайте файл `.env`:
```bash
cp .env.example .env
# Отредактируйте .env и добавьте ваш ключ
```

## 🎯 Быстрый старт

### 1. Тестирование базовой функциональности

```bash
python gigachat.py
```

### 2. Запуск прокси-сервера

```bash
python start_proxy.py
```

Сервер будет доступен по адресу: `http://localhost:4000`

### 3. Тестирование интеграции с Cline

```bash
python test_cline_integration.py
```

### 4. Интерактивные примеры

```bash
python examples.py
```

## 🔧 Использование

### Через OpenAI API (рекомендуется)

После запуска прокси-сервера:

```python
import openai

# Настройка клиента
client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="any-key"  # Может быть любым, токен управляется автоматически
)

# Запрос к GigaChat
response = client.chat.completions.create(
    model="gigachat",  # или gigachat-pro, gigachat-max
    messages=[
        {"role": "user", "content": "Привет! Как дела?"}
    ]
)

print(response.choices[0].message.content)
```

### Через curl

```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{
    "model": "gigachat",
    "messages": [
      {"role": "user", "content": "Привет, GigaChat!"}
    ]
  }'
```

### Прямое использование LiteLLM

```python
import litellm
from src.core.token_manager import get_gigachat_token
from src.callbacks.token_callback import setup_litellm_gigachat_integration

# Настройка интеграции
setup_litellm_gigachat_integration()

# Получение токена (автоматически обновляется)
token = get_gigachat_token()

# Запрос
response = litellm.completion(
    model="openai/GigaChat",
    api_base="https://gigachat.devices.sberbank.ru/api/v1",
    api_key=token,
    messages=[{"role": "user", "content": "Привет!"}]
)
```

## 🤖 Полный гайд по использованию GigaChat с Cline

Этот раздел содержит пошаговую инструкцию по настройке и использованию GigaChat с AI-ассистентом Cline.

### Шаг 1: Регистрация и получение ключа на developers.sber.ru

#### 1.1 Регистрация в GigaChat API

1. **Перейдите на сайт**: [developers.sber.ru](https://developers.sber.ru/)
2. **Войдите в систему** через Сбер ID или зарегистрируйтесь
3. **Перейдите в Studio**: Нажмите "Перейти в Studio" или откройте [developers.sber.ru/studio](https://developers.sber.ru/studio)

#### 1.2 Создание проекта GigaChat

1. **Создайте workspace** (если еще не создан):
   - Нажмите "Создать workspace"
   - Введите название (например, "My AI Projects")
   - Выберите тип "Персональный"

2. **Создайте проект**:
   - В workspace нажмите "Создать проект"
   - Выберите "GigaChat API"
   - Введите название проекта (например, "Cline Integration")
   - Нажмите "Создать"

#### 1.3 Получение Authorization Key

1. **Откройте проект GigaChat API**
2. **Перейдите в "Настройки API"** (вкладка слева)
3. **Получите ключ**:
   - Нажмите кнопку "Получить ключ" или "Создать ключ"
   - Выберите область действия (scope):
     - ✅ `GIGACHAT_API_PERS` - для персонального использования
     - ✅ `GIGACHAT_API_B2B` - для бизнес-использования (если доступно)
   - Нажмите "Создать"

4. **Скопируйте Authorization Key**:
   - Ключ будет показан в формате Base64
   - **ВАЖНО**: Сохраните ключ в безопасном месте, он больше не будет показан
   - Ключ выглядит примерно так: `NTkxNjQ5NzYtZjU5Ni00ZGY4LWE4YjMtNzQyZDQwYmY4Yjk2OmY4ZjQyNzQ5LWY5ZDMtNGRhNy1hMzQyLTQyZGY4Yjk2NzQyZA==`

### Шаг 2: Установка и настройка проекта

#### 2.1 Клонирование и установка

```bash
# Клонируйте репозиторий (или скачайте файлы)
git clone <repository-url>
cd litellm-gigachat

# Установите зависимости
pip install -r requirements.txt
```

#### 2.2 Настройка переменной окружения

**Вариант 1: Через переменную окружения (рекомендуется)**
```bash
export GIGACHAT_AUTH_KEY="ваш_authorization_key_здесь"
```

**Вариант 2: Через файл .env**
```bash
# Создайте файл .env
cp .env.example .env

# Отредактируйте .env и добавьте ваш ключ
echo "GIGACHAT_AUTH_KEY=ваш_authorization_key_здесь" > .env
```

#### 2.3 Проверка настройки

```bash
# Проверьте, что ключ установлен
echo $GIGACHAT_AUTH_KEY

# Протестируйте базовую функциональность
python gigachat.py
```

### Шаг 3: Запуск прокси-сервера

```bash
# Запустите прокси-сервер
python start_proxy.py
```

Вы должны увидеть:
```
✅ Российский корневой сертификат уже установлен
🚀 Запуск LiteLLM прокси сервера...
📡 Сервер запущен на http://localhost:4000
🔑 Автоматическое управление токенами GigaChat активировано
📝 Обработчик преобразования контента активирован
```

### Шаг 4: Настройка Cline

#### 4.1 Открытие настроек Cline

1. **Откройте VS Code** с установленным расширением Cline
2. **Откройте настройки Cline**:
   - Нажмите `Cmd+Shift+P` (Mac) или `Ctrl+Shift+P` (Windows/Linux)
   - Введите "Cline: Open Settings"
   - Или нажмите на иконку шестеренки в панели Cline

#### 4.2 Настройка API Provider

В настройках Cline укажите:

```
API Provider: OpenAI Compatible
Base URL: http://localhost:4000
API Key: gigachat-key
Model: gigachat
```

**Подробные настройки:**

1. **API Provider**: Выберите "OpenAI Compatible" из выпадающего списка
2. **Base URL**: Введите `http://localhost:4000` (без слэша в конце)
3. **API Key**: Введите любое значение, например `gigachat-key` (токен управляется автоматически)
4. **Model**: Выберите одну из моделей:
   - `gigachat` - основная модель (GigaChat-2-Max)
   - `gigachat-pro` - продвинутая модель (GigaChat-2-Pro)
   - `gigachat-max` - модель с максимальными возможностями

#### 4.3 Дополнительные настройки (опционально)

- **Temperature**: 0.7 (для баланса между креативностью и точностью)
- **Max Tokens**: 4000 (максимальная длина ответа)
- **Timeout**: 60 секунд

### Шаг 5: Тестирование интеграции

#### 5.1 Автоматический тест

```bash
# Запустите тест интеграции с Cline
python test_cline_integration.py
```

Успешный результат:
```
🧪 Тестирование интеграции Cline с GigaChat
✅ Прокси-сервер доступен
 Тест 1: Простой запрос
✅ Простой запрос успешно обработан!
📋 Тест 2: Cline-подобный запрос с массивами контента
✅ Запрос успешно обработан!
🇷🇺 Ответ содержит русские символы - интеграция работает корректно
🎉 Все тесты пройдены! Интеграция с Cline работает корректно.
```

#### 5.2 Ручное тестирование в Cline

1. **Откройте Cline** в VS Code
2. **Отправьте тестовое сообщение**:
   ```
   Привет! Можешь помочь мне с Python кодом?
   ```
3. **Проверьте ответ** - GigaChat должен ответить на русском языке

### Шаг 6: Использование GigaChat в Cline

#### 6.1 Основные возможности

После настройки вы можете использовать все возможности Cline с GigaChat:

- **Генерация кода** на Python, JavaScript, и других языках
- **Анализ и рефакторинг** существующего кода
- **Создание документации** и комментариев
- **Отладка и исправление** ошибок
- **Создание тестов** и примеров использования

#### 6.2 Примеры запросов

**Создание Python функции:**
```
Создай функцию для сортировки списка словарей по ключу
```

**Анализ кода:**
```
Проанализируй этот код и предложи улучшения:
[вставьте код]
```

**Создание документации:**
```
Создай README для этого проекта с описанием всех функций
```

#### 6.3 Особенности работы с русским языком

GigaChat отлично понимает русский язык, поэтому вы можете:

- Писать запросы на русском языке
- Получать ответы на русском языке
- Просить создать комментарии к коду на русском
- Генерировать документацию на русском языке

### Шаг 7: Мониторинг и отладка

#### 7.1 Проверка статуса

```bash
# Проверьте статус токена
python -c "
from src.core.token_manager import get_global_token_manager
manager = get_global_token_manager()
info = manager.get_token_info()
print(f'Токен активен: {info[\"has_token\"]}')
print(f'Истекает через: {info[\"expires_in_seconds\"]} сек')
"
```

#### 7.2 Просмотр логов

```bash
# Включите подробные логи при запуске прокси
PYTHONPATH=. python start_proxy.py --verbose
```

#### 7.3 Статистика обработки

```bash
# Проверьте статистику обработки контента
python -c "
from src.callbacks.content_handler import get_flatten_content_stats
stats = get_flatten_content_stats()
print(f'Обработано запросов: {stats[\"processed_requests\"]}')
print(f'Преобразовано сообщений: {stats[\"conversion_stats\"][\"converted_messages\"]}')
"
```

### Шаг 8: Устранение проблем

#### 8.1 Проблема: "Authorization key не найден"

**Решение:**
```bash
# Проверьте переменную окружения
echo $GIGACHAT_AUTH_KEY

# Если пустая, установите заново
export GIGACHAT_AUTH_KEY="ваш_ключ_здесь"
```

#### 8.2 Проблема: "Connection refused" в Cline

**Решение:**
1. Убедитесь, что прокси запущен: `python start_proxy.py`
2. Проверьте URL в настройках Cline: `http://localhost:4000`
3. Проверьте доступность: `curl http://localhost:4000/health`

#### 8.3 Проблема: "invalid JSON syntax" в Cline

**Решение:**
Эта проблема решена автоматически через `FlattenContentHandler`. Если все еще возникает:

1. Перезапустите прокси: `python start_proxy.py`
2. Проверьте тест: `python test_cline_integration.py`
3. Убедитесь, что в `config.yml` включен `flatten_content.flatten_content_handler_instance`

#### 8.4 Проблема: Медленные ответы

**Решение:**
1. Проверьте интернет-соединение
2. Попробуйте другую модель (например, `gigachat` вместо `gigachat-max`)
3. Уменьшите `max_tokens` в настройках Cline

### Шаг 9: Продвинутые настройки

#### 9.1 Настройка разных моделей для разных задач

В Cline можно быстро переключаться между моделями:

- **gigachat** - для общих задач и быстрых ответов
- **gigachat-pro** - для сложных задач программирования
- **gigachat-max** - для максимально качественных ответов

#### 9.2 Настройка температуры

- **0.1-0.3** - для точных, детерминированных ответов (код, документация)
- **0.5-0.7** - для сбалансированных ответов (общие задачи)
- **0.8-1.0** - для креативных ответов (идеи, творческие задачи)

#### 9.3 Автозапуск прокси

Создайте скрипт для автозапуска:

```bash
#!/bin/bash
# start_gigachat.sh
cd /path/to/litellm-gigachat
export GIGACHAT_AUTH_KEY="ваш_ключ"
python start_proxy.py
```

### Шаг 10: Заключение

После выполнения всех шагов у вас будет:

✅ **Настроенный GigaChat API** с валидным ключом  
✅ **Работающий прокси-сервер** с автоматическим обновлением токенов  
✅ **Интегрированный Cline** с поддержкой русского языка  
✅ **Автоматическое преобразование контента** для совместимости  
✅ **Мониторинг и отладка** для контроля работы системы  

Теперь вы можете полноценно использовать GigaChat через Cline для разработки, анализа кода и других AI-задач на русском языке!

### Быстрая справка по командам

```bash
# Запуск прокси
python start_proxy.py

# Тестирование
python test_cline_integration.py

# Проверка статуса
python gigachat.py

# Примеры использования
python examples.py

# Проверка переменной окружения
echo $GIGACHAT_AUTH_KEY
```

## 📊 Доступные модели

| Модель в API   | Реальная модель GigaChat | Описание |
|----------------|--------------------------|----------|
| `gigachat`     | `GigaChat-2-Max` | Основная модель с максимальными возможностями |
| `gigachat-pro` | `GigaChat-2-Pro` | Продвинутая модель для сложных задач |
| `gigachat-max` | `GigaChat-2-Max` | Модель с максимальными возможностями |

## 🏗️ Архитектура проекта

### Структура проекта

```
litellm-gigachat/
├── README.md                   # Основная документация
├── requirements.txt            # Зависимости Python
├── .env.example               # Пример переменных окружения
├── config.yml                 # Конфигурация LiteLLM
├── start_proxy.py             # Точка входа для прокси-сервера
├── gigachat.py               # Точка входа для тестирования
├── examples.py               # Точка входа для примеров
│
├── src/                       # Основной код
│   ├── __init__.py
│   ├── core/                  # Ядро системы
│   │   ├── __init__.py
│   │   ├── token_manager.py   # Управление токенами
│   │   └── gigachat_client.py # Клиент GigaChat
│   │
│   ├── callbacks/             # LiteLLM callbacks
│   │   ├── __init__.py
│   │   ├── token_callback.py  # Автоматическое обновление токенов
│   │   └── content_handler.py # Преобразование контента для Cline
│   │
│   └── proxy/                 # Прокси сервер
│       ├── __init__.py
│       └── server.py          # LiteLLM прокси с интеграцией
│
├── tests/                     # Тесты
│   ├── __init__.py
│   ├── test_basic_functionality.py
│   ├── test_content_handler.py
│   ├── test_cline_integration.py
│   └── test_proxy.py
│
├── examples/                  # Примеры использования
│   ├── __init__.py
│   └── basic_usage.py
│
├── docs/                      # Документация
    └── test_requests.md
```

### Основные компоненты

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Клиент        │    │   LiteLLM Proxy  │    │   GigaChat API  │
│ (Cline/curl/SDK)│────│   + Callbacks    │────│                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   TokenManager   │
                       │ + ContentHandler │
                       └──────────────────┘
```

### Ключевые модули

| Модуль | Назначение |
|--------|------------|
| `src.core.token_manager` | **Управление токенами** - автоматическое обновление и кэширование |
| `src.callbacks.token_callback` | **Интеграция с LiteLLM** - автоматическая подстановка токенов |
| `src.callbacks.content_handler` | **Обработка контента** - преобразование массивов для совместимости с Cline |
| `src.proxy.server` | **Прокси сервер** - LiteLLM прокси с автоматической настройкой сертификатов |
| `config.yml` | **Конфигурация** - настройки моделей и callbacks |
| `examples.basic_usage` | **Примеры использования** - интерактивные демонстрации |
| `tests.test_cline_integration` | **Тестирование Cline** - проверка совместимости |

### Компоненты системы

#### 1. TokenManager
- Автоматическое обновление токенов за 5 минут до истечения
- Thread-safe операции с мьютексами
- Обработка ошибок авторизации и retry-логика
- Глобальный менеджер для всего приложения

#### 2. GigaChatTokenCallback
- Перехват запросов LiteLLM для подстановки токенов
- Автоматическая инвалидация при ошибках 401
- Прозрачная интеграция без изменения кода

#### 3. FlattenContentHandler
- Преобразование массивов контента в строки для GigaChat API
- Умная обработка различных типов контента (текст, изображения)
- Детальное логирование и статистика обработки
- Совместимость с Cline и другими AI-ассистентами

#### 4. Автоматическая настройка сертификатов
- Загрузка российских корневых сертификатов при первом запуске
- Проверка существующих сертификатов
- Обработка ошибок загрузки и записи

## 🧪 Тестирование

### Базовые тесты

```bash
# Тест базовой функциональности
python gigachat.py

# Тест управления токенами
python test_basic_functionality.py

# Тест обработки контента
python test_flatten_content.py

# Тест интеграции с Cline
python test_cline_integration.py
```

### Тестирование прокси

```bash
# Запуск прокси в одном терминале
python start_proxy.py

# Тестирование в другом терминале
python test_proxy.py
```

### Интерактивные примеры

```bash
python examples.py
```

Доступные примеры:
1. Базовый чат
2. Разные модели GigaChat
3. Диалог с контекстом
4. Управление токенами
5. Обработка ошибок
6. Потоковый ответ
7. Параметры запроса
8. Нагрузочное тестирование

## 🔧 Конфигурация

### Переменные окружения

| Переменная | Описание | Обязательная |
|------------|----------|--------------|
| `GIGACHAT_AUTH_KEY` | Authorization Key в формате Base64 | Да |

### Файл .env (опционально)

```bash
# Скопируйте пример и отредактируйте
cp .env.example .env
```

### Настройка логирования

```python
import logging

# Включить debug-логи
logging.basicConfig(level=logging.DEBUG)

# Или только для конкретных модулей
logging.getLogger('token_manager').setLevel(logging.DEBUG)
logging.getLogger('flatten_content').setLevel(logging.DEBUG)
```

## 📈 Мониторинг и отладка

### Проверка статуса токена

```python
from token_manager import get_global_token_manager

manager = get_global_token_manager()
info = manager.get_token_info()

print(f"Есть токен: {info['has_token']}")
print(f"Истекает через: {info['expires_in_seconds']} секунд")
print(f"Токен истек: {info['is_expired']}")
```

### Статистика обработки контента

```python
from flatten_content import get_flatten_content_stats

stats = get_flatten_content_stats()
print(f"Обработано запросов: {stats['processed_requests']}")
print(f"Преобразовано сообщений: {stats['conversion_stats']['converted_messages']}")
```

### Принудительное обновление токена

```python
from token_manager import get_global_token_manager

manager = get_global_token_manager()
new_token = manager.get_token(force_refresh=True)
```

## 🚨 Устранение неполадок

### Ошибка "Authorization key не найден"

```bash
# Проверьте переменную окружения
echo $GIGACHAT_AUTH_KEY

# Или установите её
export GIGACHAT_AUTH_KEY="ваш_ключ"
```

### Ошибка 401 (Unauthorized)

- Проверьте правильность Authorization Key
- Убедитесь, что ключ не истек в личном кабинете
- Проверьте область действия (scope) ключа

### Ошибки сети

- Проверьте доступность `ngw.devices.sberbank.ru:9443`
- Убедитесь в наличии интернет-соединения
- Проверьте настройки прокси/файрвола

### Проблемы с сертификатами

```bash
# Ручная установка российского сертификата
curl -k "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt" -w "\n" >> $(python -m certifi)
```

## 🚀 Развертывание

### Локальное развертывание

```bash
# 1. Клонирование и установка
git clone <repository>
cd litellm-gigachat
pip install -r requirements.txt

# 2. Настройка
export GIGACHAT_AUTH_KEY="ваш_ключ"

# 3. Тестирование
python gigachat.py

# 4. Запуск прокси
python start_proxy.py
```

## 📚 Примеры использования

### Простой чат

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="any-key"
)

response = client.chat.completions.create(
    model="gigachat",
    messages=[{"role": "user", "content": "Привет!"}]
)

print(response.choices[0].message.content)
```

### Диалог с контекстом

```python
messages = [
    {"role": "user", "content": "Меня зовут Алексей"},
]

response = client.chat.completions.create(
    model="gigachat",
    messages=messages
)

messages.append({"role": "assistant", "content": response.choices[0].message.content})
messages.append({"role": "user", "content": "Как меня зовут?"})

response = client.chat.completions.create(
    model="gigachat",
    messages=messages
)
```

### Потоковый ответ

```python
response = client.chat.completions.create(
    model="gigachat",
    messages=[{"role": "user", "content": "Расскажи историю"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='', flush=True)
```

### Настройка параметров

```python
response = client.chat.completions.create(
    model="gigachat-pro",
    messages=[{"role": "user", "content": "Придумай название для стартапа"}],
    temperature=0.9,  # Более креативные ответы
    max_tokens=100,   # Ограничение длины
)
```