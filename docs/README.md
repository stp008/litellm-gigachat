# 📚 Документация LiteLLM GigaChat Integration

Добро пожаловать в документацию проекта **LiteLLM GigaChat Integration** - полнофункциональной интеграции российской языковой модели Сбер GigaChat с экосистемой LiteLLM.

## 🚀 Быстрая навигация

### 📖 Основная документация
- **[Быстрый старт](../README.md)** - краткое введение и установка
- **[Интеграция с Cline](GIGACHAT_COMPATIBILITY.md)** - подробное руководство по настройке AI-ассистента
- **[Часто задаваемые вопросы](FAQ.md)** - ответы на популярные вопросы

### 🔧 Техническая документация
- **[Совместимость API](GIGACHAT_COMPATIBILITY.md)** - трансформации OpenAI ↔ GigaChat
- **[Тестовые запросы](TEST_REQUESTS.md)** - примеры API вызовов
- **[История изменений](CHANGELOG.md)** - все версии и обновления

### ⚙️ Настройка и развертывание
- **[Описание репозитория](DESCRIPTION.md)** - настройки GitHub
- **[Скриншоты настроек](images/)** - визуальные инструкции

## 🎯 Что такое LiteLLM GigaChat Integration?

Это готовое решение для подключения российской языковой модели **Сбер GigaChat** через стандартный **OpenAI-совместимый интерфейс**. Проект решает проблемы несовместимости форматов API и обеспечивает бесшовную интеграцию с существующими инструментами.

### ✨ Ключевые особенности

- 🔐 **Автоматическое управление токенами**
- 🤖 **Полная поддержка Cline**
- 🔄 **Двунаправленный трансформер** - OpenAI ↔ GigaChat форматы
- 🌊 **Streaming поддержка** - потоковые ответы в реальном времени
- 🔒 **Автоматические сертификаты** - российские корневые сертификаты

## 🚀 Быстрый старт

### 1. Установка
```bash
git clone https://github.com/stp008/litellm-gigachat.git
cd litellm-gigachat
pip install -r requirements.txt
```

### 2. Настройка
```bash
export GIGACHAT_AUTH_KEY="ваш_authorization_key"
```

### 3. Запуск
```bash
python start_proxy.py
```

### 4. Использование
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
```

## 🎯 Популярные сценарии использования

### 🤖 Интеграция с AI-ассистентами
- **Cline**
- **Continue.dev** - аналогичная настройка через OpenAI Compatible
- **Cursor** - использование через прокси-сервер

## 🔗 Полезные ссылки

### Официальные ресурсы
- [GitHub репозиторий](https://github.com/stp008/litellm-gigachat)
- [GigaChat API](https://developers.sber.ru/portal/products/gigachat-api)
- [LiteLLM документация](https://docs.litellm.ai/)

### Сообщество
- [Cline GitHub](https://github.com/cline/cline) - AI-ассистент для VS Code
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference) - совместимый интерфейс

---

**Последнее обновление**: 9 января 2025  
**Версия документации**: 1.2.0  
**Поддерживаемые версии**: Python 3.8+, LiteLLM 1.65.1+
