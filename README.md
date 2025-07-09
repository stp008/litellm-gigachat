# LiteLLM GigaChat Integration | Полная интеграция API Сбер GigaChat с LiteLLM

[![GitHub stars](https://img.shields.io/github/stars/stp008/litellm-gigachat?style=social)](https://github.com/stp008/litellm-gigachat/stargazers)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![LiteLLM](https://img.shields.io/badge/LiteLLM-1.65.1-green.svg)](https://github.com/BerriAI/litellm)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GigaChat](https://img.shields.io/badge/GigaChat-API-red.svg)](https://developers.sber.ru/portal/products/gigachat-api)

**Полнофункциональная интеграция GigaChat API с LiteLLM** - готовое решение для подключения российской языковой модели Сбер GigaChat через стандартный OpenAI-совместимый интерфейс. Включает автоматическое обновление токенов, преобразование контента и полную совместимость с AI-ассистентом Cline.

**Ключевые слова:** `litellm gigachat`, `gigachat api integration`, `сбер gigachat proxy`, `gigachat openai compatibility`, `cline gigachat`, `russian ai api`

## 📚 Документация

**[📖 Полная документация](docs/README.md)** | **[❓ FAQ](docs/FAQ.md)** **[🔧 API Reference](docs/TEST_REQUESTS.md)**

## 🚀 Основные возможности

- ✅ **Автоматическое обновление токенов**
- ✅ **Автоматическая настройка сертификатов**
- ✅ **Совместимость с Cline** 
- ✅ **Streaming поддержка**

## 📦 Быстрая установка

```bash
# 1. Клонирование репозитория
git clone https://github.com/stp008/litellm-gigachat.git
cd litellm-gigachat

# 2. Установка зависимостей
pip install -r requirements.txt

# 3. Настройка ключа API
export GIGACHAT_AUTH_KEY="ваш_authorization_key"

# 4. Запуск прокси-сервера
python start_proxy.py
```

## 🎯 Быстрый старт

### Использование через OpenAI API

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

### Использование через Cline

Допустимо использовать сервер как в качестве OpenAI совместимого провайдера, так и в качестве LiteLLM провайдера. В случае использования второго варианта появляется больше доступных опций.

##### Настройки OpenAI Compatible провайдера:
<img src="docs/images/cline-settings-openai.png" alt="Настройки Cline с OpenAI совместимостью" width="400">

##### Настройка LiteLLM провайдера:
<img src="docs/images/cline-settings-litellm.png" alt="Настройки Cline через LiteLLM" width="400">

В настройках Cline укажите следующие параметры:

**Основные настройки:**
1. **API Provider**: Выберите `OpenAI Compatible` или `LiteLLM` из выпадающего списка
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

## 📊 Доступные модели

| Модель API | Описание |
|------------|----------|
| `gigachat` | Основная модель для общих задач |
| `gigachat-pro` | Продвинутая модель для сложных задач |
| `gigachat-max` | Модель с максимальными возможностями |

## 🧪 Тестирование

```bash
# Базовая функциональность
python gigachat.py

# Интеграция с Cline
python test_cline_integration.py

# Интерактивные примеры
python examples.py
```

## 🚨 Устранение неполадок

### Ошибка "Authorization key не найден"
```bash
export GIGACHAT_AUTH_KEY="ваш_ключ"
```

### Проблемы с Cline
- Убедитесь, что прокси запущен: `python start_proxy.py`
- Проверьте URL: `http://localhost:4000`
- Тест интеграции: `python test_cline_integration.py`

Полное руководство: **[❓ FAQ](docs/FAQ.md)**

## 🔗 Полезные ссылки

- **[📚 Полная документация](docs/README.md)** - подробное руководство
- **[❓ FAQ](docs/FAQ.md)** - часто задаваемые вопросы
- **[🔧 API Reference](docs/TEST_REQUESTS.md)** - примеры запросов
- **[📝 История изменений](docs/CHANGELOG.md)** - все версии
- **[🤝 Участие в проекте](docs/CONTRIBUTING.md)** - как внести вклад

---

**Лицензия**: MIT | **Поддерживаемые версии**: Python 3.8+ | **Последнее обновление**: 9 января 2025
