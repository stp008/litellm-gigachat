# Часто задаваемые вопросы (FAQ) - LiteLLM GigaChat Integration

## 🔍 Общие вопросы

### Что такое LiteLLM GigaChat Integration?

**LiteLLM GigaChat Integration** - это готовое решение для подключения российской языковой модели Сбер GigaChat через стандартный OpenAI-совместимый интерфейс. Проект обеспечивает полную совместимость GigaChat API с экосистемой OpenAI, включая автоматическое управление токенами и преобразование форматов данных.

### Зачем нужна интеграция GigaChat с LiteLLM?

GigaChat API имеет отличия от стандарта OpenAI:
- Использует `functions` вместо `tools`
- Использует `function_call` вместо `tool_calls`
- Не поддерживает массивы в поле `content`
- Требует регулярного обновления токенов

Наша интеграция решает все эти проблемы автоматически.

### Поддерживается ли работа с AI-ассистентом Cline?

Да! Проект специально оптимизирован для работы с Cline и решает проблему "invalid JSON syntax", которая часто возникает при использовании GigaChat с AI-ассистентами.

## 🚀 Установка и настройка

### Как получить Authorization Key для GigaChat?

1. Зарегистрируйтесь на [developers.sber.ru](https://developers.sber.ru/)
2. Создайте workspace и проект GigaChat API
3. В настройках API нажмите "Получить ключ"
4. Выберите scope: `GIGACHAT_API_PERS` или `GIGACHAT_API_B2B`
5. Скопируйте полученный ключ в формате Base64

### Какие зависимости нужно установить?

Все зависимости указаны в `requirements.txt`:
```bash
pip install -r requirements.txt
```

Основные компоненты:
- `litellm==1.65.1` - основная библиотека
- `requests` - для HTTP запросов
- `certifi` - для работы с сертификатами
- `python-dotenv` - для переменных окружения

### Как настроить переменные окружения?

**Вариант 1 (рекомендуется):**
```bash
export GIGACHAT_AUTH_KEY="ваш_authorization_key"
```

**Вариант 2:**
```bash
cp .env.example .env
# Отредактируйте .env файл
```

## 🔧 Использование

### Как запустить прокси-сервер?

```bash
python start_proxy.py
```

Сервер будет доступен по адресу `http://localhost:4000`

### Как использовать через OpenAI SDK?

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="any-key"  # Может быть любым
)

response = client.chat.completions.create(
    model="gigachat",
    messages=[{"role": "user", "content": "Привет!"}]
)
```

### Какие модели доступны?

| Модель в API | Реальная модель | Описание |
|--------------|-----------------|----------|
| `gigachat` | GigaChat-2-Max | Основная модель |
| `gigachat-pro` | GigaChat-2-Pro | Продвинутая модель |
| `gigachat-max` | GigaChat-2-Max | Максимальные возможности |

### Поддерживается ли streaming?

Да, полностью поддерживается:

```python
response = client.chat.completions.create(
    model="gigachat",
    messages=[{"role": "user", "content": "Расскажи историю"}],
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end='')
```

## 🤖 Интеграция с Cline

### Как настроить Cline для работы с GigaChat?

1. Запустите прокси: `python start_proxy.py`
2. В настройках Cline выберите `OpenAI Compatible`
3. Base URL: `http://localhost:4000`
4. API Key: любое значение (например, `gigachat-key`)
5. Model: `gigachat`

### Почему возникает ошибка "invalid JSON syntax" в Cline?

Эта ошибка возникает из-за несовместимости форматов GigaChat и OpenAI. Наш проект автоматически решает эту проблему через `FlattenContentHandler`, который преобразует массивы content в строки.

### Можно ли использовать разные модели GigaChat в Cline?

Да, вы можете переключаться между моделями:
- `gigachat` - для общих задач
- `gigachat-pro` - для сложного программирования
- `gigachat-max` - для максимального качества

## 🔍 Устранение неполадок

### Ошибка "Authorization key не найден"

**Причины:**
- Переменная окружения не установлена
- Неправильное имя переменной
- Ключ не сохранился в сессии

**Решение:**
```bash
echo $GIGACHAT_AUTH_KEY  # Проверить
export GIGACHAT_AUTH_KEY="ваш_ключ"  # Установить
```

### Ошибка 401 (Unauthorized)

**Причины:**
- Неправильный Authorization Key
- Истекший ключ
- Неправильный scope

**Решение:**
1. Проверьте ключ в личном кабинете
2. Создайте новый ключ при необходимости
3. Убедитесь в правильности scope

### Ошибка "Connection refused" в Cline

**Причины:**
- Прокси-сервер не запущен
- Неправильный URL в настройках
- Блокировка портов

**Решение:**
1. Запустите прокси: `python start_proxy.py`
2. Проверьте URL: `http://localhost:4000`
3. Проверьте доступность: `curl http://localhost:4000/health`

### Медленные ответы от GigaChat

**Причины:**
- Медленное интернет-соединение
- Высокая нагрузка на API
- Большие значения max_tokens

**Решение:**
1. Проверьте интернет-соединение
2. Попробуйте модель `gigachat` вместо `gigachat-max`
3. Уменьшите `max_tokens` в запросах

### Проблемы с сертификатами

**Ошибка:** SSL certificate verify failed

**Решение:**
```bash
# Автоматическая установка (выполняется при запуске)
python -c "from src.core.gigachat_client import install_russian_certificate; install_russian_certificate()"

# Ручная установка
curl -k "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt" -w "\n" >> $(python -m certifi)
```

## 📊 Мониторинг и отладка

### Как проверить статус токена?

```python
from src.litellm_gigachat.core import get_global_token_manager

manager = get_global_token_manager()
info = manager.get_token_info()

print(f"Токен активен: {info['has_token']}")
print(f"Истекает через: {info['expires_in_seconds']} сек")
```

### Как включить подробные логи?

```bash
# При запуске прокси
PYTHONPATH=. python start_proxy.py --verbose

# В коде Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Как получить статистику обработки?

```python
from src.litellm_gigachat.callbacks.content_handler import get_flatten_content_stats

stats = get_flatten_content_stats()
print(f"Обработано запросов: {stats['processed_requests']}")
print(f"Преобразовано сообщений: {stats['conversion_stats']['converted_messages']}")
```

## 🔄 Сравнение с альтернативами

### В чем отличие от прямого использования GigaChat API?

| Аспект | Прямое API | LiteLLM Integration |
|--------|------------|-------------------|
| Совместимость с OpenAI | ❌ | ✅ |
| Автообновление токенов | ❌ | ✅ |
| Поддержка Cline | ❌ | ✅ |
| Преобразование форматов | ❌ | ✅ |
| Простота использования | ⚠️ | ✅ |

### Почему не использовать другие обертки?

Наше решение специально оптимизировано для:
- Российского рынка и GigaChat API
- Работы с AI-ассистентами (Cline)
- Автоматического управления токенами
- Полной совместимости с OpenAI экосистемой

## 🚀 Продвинутое использование

### Можно ли использовать с другими AI-ассистентами?

Да, любые инструменты, совместимые с OpenAI API, будут работать:
- Continue.dev
- Cursor
- GitHub Copilot (через прокси)
- Собственные приложения

### Как настроить автозапуск прокси?

Создайте скрипт:
```bash
#!/bin/bash
cd /path/to/litellm-gigachat
export GIGACHAT_AUTH_KEY="ваш_ключ"
python start_proxy.py
```

### Поддерживается ли развертывание в продакшене?

Да, но учтите:
- Настройте HTTPS
- Используйте переменные окружения для ключей
- Настройте мониторинг и логирование
- Рассмотрите использование Docker

### Как интегрировать в существующий проект?

```python
# Добавьте в ваш проект
from src.litellm_gigachat.core import get_gigachat_token
from src.litellm_gigachat.callbacks import setup_litellm_gigachat_integration

# Настройка
setup_litellm_gigachat_integration()

# Использование
import litellm

response = litellm.completion(
    model="openai/GigaChat",
    api_base="https://gigachat.devices.sberbank.ru/api/v1",
    api_key=get_gigachat_token(),
    messages=[{"role": "user", "content": "Привет!"}]
)
```
