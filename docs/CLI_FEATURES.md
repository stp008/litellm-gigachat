# CLI Features для litellm-gigachat

## 🌐 Глобальные опции

Доступны для всех команд:

- `--version` - Показать версию и выйти
- `-v, --verbose` - Подробная информация о выполнении
- `-d, --debug` - Максимальная отладка с сохранением логов
- `--help` - Показать справку и выйти

## 📋 Общая справка

При вызове `litellm-gigachat --help` отображается чистый, профессиональный интерфейс:
- 🌐 Глобальные опции с улучшенными описаниями
- 📚 Полный список команд (включая новые)
- Краткое описание каждой команды
- Инструкция для получения детальной справки по каждой команде

### Изменения после рефакторинга:
- ✅ Убрано дублирование информации в help
- ✅ Чистый вывод без избыточного текста
- ✅ Добавлены новые команды для удобства
- ✅ Улучшены описания опций
- ✅ Стандартный формат Click без кастомных секций

## Команды

### 1. `start` - Запустить LiteLLM прокси-сервер для GigaChat

**Использование:**
```bash
litellm-gigachat start [OPTIONS]
```

**Опции:**
- `--host TEXT` - Хост для прокси-сервера [default: 0.0.0.0]
- `--port INTEGER` - Порт для прокси-сервера [default: 4000]
- `--config TEXT` - Путь к файлу конфигурации [default: config.yml]

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

### 2. `test` - Протестировать подключение к GigaChat

**Использование:**
```bash
litellm-gigachat test [OPTIONS]
```

**Опции:**
- `--timeout INTEGER` - Таймаут для тестирования в секундах [default: 30]

**Примеры:**
```bash
# Базовое тестирование
litellm-gigachat test

# Тестирование с увеличенным таймаутом
litellm-gigachat test --timeout 60

# Подробное тестирование
litellm-gigachat --verbose test
```

### 3. `token-info` - Показать информацию о текущем токене

**Использование:**
```bash
litellm-gigachat token-info [OPTIONS]
```

**Опции:**
- `--format [json|table]` - Формат вывода [default: table]

**Примеры:**
```bash
# Показать информацию о токене
litellm-gigachat token-info

# Вывод в JSON формате
litellm-gigachat token-info --format json

# Подробная информация
litellm-gigachat --verbose token-info
```

### 4. `refresh-token` - Принудительно обновить токен

**Использование:**
```bash
litellm-gigachat refresh-token [OPTIONS]
```

**Опции:**
- `--force` - Принудительно обновить токен даже если текущий еще действителен

**Примеры:**
```bash
# Обновить токен если нужно
litellm-gigachat refresh-token

# Принудительно обновить токен
litellm-gigachat refresh-token --force

# Подробное обновление
litellm-gigachat --verbose refresh-token --force
```

### 5. `examples` - Запустить интерактивные примеры использования

**Использование:**
```bash
litellm-gigachat examples [OPTIONS]
```

**Опции:**
- `--list` - Показать список доступных примеров
- `--run TEXT` - Запустить конкретный пример по имени

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

### 6. `version` - Показать версию пакета и компонентов

**Использование:**
```bash
litellm-gigachat version [OPTIONS]
```

**Опции:**
- `--components` - Показать версии всех компонентов
- `--json-output` - Вывод в формате JSON
- `--check-updates` - Проверить доступность обновлений

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

### 7. `help-examples` - Показать примеры использования команд ⭐ НОВАЯ

**Использование:**
```bash
litellm-gigachat help-examples
```

**Описание:**
Отображает структурированные примеры использования всех команд, сгруппированные по категориям:
- Запуск сервера
- Тестирование
- Управление токенами
- Примеры и версия
- Режимы работы

**Примеры:**
```bash
# Показать все примеры использования
litellm-gigachat help-examples

# Показать примеры в verbose режиме
litellm-gigachat --verbose help-examples
```

### 8. `env-check` - Проверить переменные окружения и их статус ⭐ НОВАЯ

**Использование:**
```bash
litellm-gigachat env-check [OPTIONS]
```

**Опции:**
- `--format [json|table]` - Формат вывода [default: table]

**Описание:**
Проверяет все переменные окружения, необходимые для работы с GigaChat:
- Показывает статус каждой переменной (установлена/не установлена)
- Маскирует чувствительные данные (API ключи)
- Проверяет обязательные переменные
- Предоставляет рекомендации по настройке

**Примеры:**
```bash
# Проверить переменные окружения
litellm-gigachat env-check

# Вывод в JSON формате
litellm-gigachat env-check --format json

# Подробная проверка с описаниями
litellm-gigachat --verbose env-check
```

## Режимы работы

### Verbose режим (`-v, --verbose`)
- Показывает дополнительную информацию
- Включает подробные логи
- Отображает расширенные таблицы и статистику

### Debug режим (`-d, --debug`)
- Включает максимально подробный вывод
- Показывает отладочную информацию
- Выводит технические детали выполнения команд
- Включает трассировку ошибок

## Примеры комбинированного использования

```bash
# Запуск сервера в debug режиме
litellm-gigachat --debug start --host localhost --port 8080

# Тестирование с подробным выводом
litellm-gigachat --verbose test --timeout 60

# Получение полной информации о версии в JSON
litellm-gigachat --debug version --components --json-output

# Принудительное обновление токена с отладкой
litellm-gigachat --debug refresh-token --force

# Запуск примера с подробным выводом
litellm-gigachat --verbose examples --run basic_usage
```

## Переменные окружения

CLI автоматически загружает переменные из `.env` файла:

- `GIGACHAT_AUTH_KEY` - Обязательная переменная с ключом авторизации
- `GIGACHAT_BASE_URL` - URL базы GigaChat API
- `GIGACHAT_SCOPE` - Область действия токена
- `GIGACHAT_VERIFY_SSL_CERTS` - Проверка SSL сертификатов

## Файлы конфигурации

По умолчанию CLI ищет файл `config.yml` в текущей директории. Можно указать альтернативный путь через параметр `--config`.

## Логирование

- В обычном режиме выводятся только основные сообщения
- В verbose режиме (`-v`) добавляются информационные сообщения
- В debug режиме (`-d`) выводятся все отладочные сообщения и трассировки ошибок
