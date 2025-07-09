---
layout: default
title: "LiteLLM GigaChat Integration - Документация"
description: "Полная интеграция российской языковой модели Сбер GigaChat с экосистемой LiteLLM. OpenAI-совместимый прокси для GigaChat API с поддержкой Cline."
keywords: "litellm, gigachat, api, proxy, ai, chatbot, sber, russian-ai, openai-compatible, cline, integration"
lang: ru
---

# 📚 LiteLLM GigaChat Integration

**Полнофункциональная интеграция российской языковой модели Сбер GigaChat с экосистемой LiteLLM**

[![GitHub stars](https://img.shields.io/github/stars/stp008/litellm-gigachat?style=social)](https://github.com/stp008/litellm-gigachat/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/stp008/litellm-gigachat?style=social)](https://github.com/stp008/litellm-gigachat/network/members)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/stp008/litellm-gigachat/blob/main/LICENSE)

## 🎯 О проекте

Готовое решение для подключения российской языковой модели **Сбер GigaChat** через стандартный **OpenAI-совместимый интерфейс**. Проект решает проблемы несовместимости форматов API и обеспечивает бесшовную интеграцию с существующими инструментами.

## ✨ Ключевые особенности

- 🔐 **Автоматическое управление токенами** - обновление каждые 30 минут
- 🤖 **Полная поддержка Cline** - без ошибок "invalid JSON syntax"
- 🔄 **Двунаправленный трансформер** - OpenAI ↔ GigaChat форматы
- 🌊 **Streaming поддержка** - потоковые ответы в реальном времени
- 📊 **Множественные модели** - GigaChat, GigaChat-Pro, GigaChat-Max
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
    messages=[{"role": "user", "content": "Привет, GigaChat!"}]
)

print(response.choices[0].message.content)
```

## 📚 Документация

<div class="docs-grid">
  <div class="docs-card">
    <h3>📖 Основная документация</h3>
    <ul>
      <li><a href="README.html">Полное руководство</a></li>
      <li><a href="FAQ.html">Часто задаваемые вопросы</a></li>
      <li><a href="CONTRIBUTING.html">Участие в проекте</a></li>
    </ul>
  </div>
  
  <div class="docs-card">
    <h3>🔧 Техническая документация</h3>
    <ul>
      <li><a href="GIGACHAT_COMPATIBILITY.html">Совместимость API</a></li>
      <li><a href="TEST_REQUESTS.html">Примеры запросов</a></li>
      <li><a href="CHANGELOG.html">История изменений</a></li>
    </ul>
  </div>
  
  <div class="docs-card">
    <h3>⚙️ Настройка и развертывание</h3>
    <ul>
      <li><a href="DESCRIPTION.html">Настройки GitHub</a></li>
      <li><a href="SEO_ACTION_PLAN.html">План продвижения</a></li>
      <li><a href="KEYWORDS.html">SEO ключевые слова</a></li>
    </ul>
  </div>
</div>

## 🤖 Интеграция с Cline

**Пошаговая настройка AI-ассистента Cline:**

1. **API Provider**: `OpenAI Compatible` или `LiteLLM`
2. **Base URL**: `http://localhost:4000`
3. **API Key**: `gigachat-key` (любое значение)
4. **Model**: `gigachat`, `gigachat-pro`, или `gigachat-max`

[📖 Подробная инструкция по настройке Cline](GIGACHAT_COMPATIBILITY.html)

## 📊 Доступные модели

| Модель API | Описание | Рекомендации |
|------------|----------|--------------|
| `gigachat` | Основная модель | Для общих задач |
| `gigachat-pro` | Продвинутая модель | Для сложных задач программирования |
| `gigachat-max` | Максимальные возможности | Для качественных ответов |

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

[❓ Полное руководство по устранению неполадок](FAQ.html)

## 🔗 Полезные ссылки

### Официальные ресурсы
- [GitHub репозиторий](https://github.com/stp008/litellm-gigachat)
- [GigaChat API](https://developers.sber.ru/portal/products/gigachat-api)
- [LiteLLM документация](https://docs.litellm.ai/)

### Сообщество
- [Cline GitHub](https://github.com/cline/cline) - AI-ассистент для VS Code
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)

## 📞 Поддержка

- **[🐛 Сообщить о проблеме](https://github.com/stp008/litellm-gigachat/issues/new/choose)**
- **[💬 Обсуждения](https://github.com/stp008/litellm-gigachat/discussions)**
- **[📧 Email поддержка](mailto:support@example.com)**

---

<div class="footer-info">
  <p><strong>Лицензия</strong>: MIT | <strong>Поддерживаемые версии</strong>: Python 3.8+ | <strong>Последнее обновление</strong>: 9 января 2025</p>
  <p>Создано с ❤️ для российского AI-сообщества</p>
</div>

<style>
.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin: 20px 0;
}

.docs-card {
  border: 1px solid #e1e4e8;
  border-radius: 8px;
  padding: 20px;
  background: #f6f8fa;
}

.docs-card h3 {
  margin-top: 0;
  color: #24292e;
}

.docs-card ul {
  list-style: none;
  padding: 0;
}

.docs-card li {
  margin: 8px 0;
}

.docs-card a {
  color: #0366d6;
  text-decoration: none;
}

.docs-card a:hover {
  text-decoration: underline;
}

.footer-info {
  text-align: center;
  margin-top: 40px;
  padding: 20px;
  background: #f6f8fa;
  border-radius: 8px;
  color: #586069;
}
</style>
