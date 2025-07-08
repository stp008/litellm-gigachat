# JSON Payload Трансформации: OpenAI ↔ GigaChat

Этот документ содержит максимально полные примеры JSON payload и их трансформации между OpenAI API и GigaChat API форматами.

## Содержание

1. [Обзор трансформаций](#обзор-трансформаций)
2. [OpenAI → GigaChat: Входящие запросы](#openai--gigachat-входящие-запросы)
3. [GigaChat → OpenAI: Исходящие ответы](#gigachat--openai-исходящие-ответы)
4. [Специальные случаи](#специальные-случаи)
5. [Streaming трансформации](#streaming-трансформации)
6. [Обработка ошибок](#обработка-ошибок)

---

## Обзор трансформаций

### Основные принципы:

**OpenAI → GigaChat:**
- `tools` → `functions`
- `tool_choice` → `function_call`
- Массивы `content` → строки
- Сохранение базовых параметров (model, temperature, max_tokens и т.д.)

**GigaChat → OpenAI:**
- `function_call` → `tool_calls`
- Генерация OpenAI-совместимых ID и метаданных
- Адаптация `finish_reason`
- Стандартизация структуры ответа

---

## OpenAI → GigaChat: Входящие запросы

### 1. Максимально полный OpenAI запрос

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "Ты полезный ассистент, который помогает пользователям с различными задачами."
    },
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Привет! Можешь помочь мне с погодой в Москве?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "https://example.com/weather-map.jpg",
            "detail": "high"
          }
        }
      ]
    },
    {
      "role": "assistant",
      "content": "Конечно! Я помогу вам узнать погоду в Москве."
    },
    {
      "role": "user",
      "content": "Какая сейчас температура?"
    }
  ],
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_current_weather",
        "description": "Получить текущую погоду в указанном городе",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "Город и страна, например 'Москва, Россия'"
            },
            "unit": {
              "type": "string",
              "enum": ["celsius", "fahrenheit"],
              "description": "Единица измерения температуры"
            }
          },
          "required": ["location"]
        }
      }
    },
    {
      "type": "function",
      "function": {
        "name": "get_weather_forecast",
        "description": "Получить прогноз погоды на несколько дней",
        "parameters": {
          "type": "object",
          "properties": {
            "location": {
              "type": "string",
              "description": "Город и страна"
            },
            "days": {
              "type": "integer",
              "description": "Количество дней для прогноза",
              "minimum": 1,
              "maximum": 7
            }
          },
          "required": ["location", "days"]
        }
      }
    }
  ],
  "tool_choice": {
    "type": "function",
    "function": {
      "name": "get_current_weather"
    }
  },
  "temperature": 0.7,
  "max_tokens": 1500,
  "top_p": 0.9,
  "frequency_penalty": 0.1,
  "presence_penalty": 0.1,
  "stop": ["\n\n", "###"],
  "stream": false,
  "user": "user-12345"
}
```

### 2. Трансформация в GigaChat формат

**Пошаговая трансформация:**

1. **Обработка messages:**
   - Массив content преобразуется в строку
   - Изображения заменяются на описание

2. **Трансформация tools → functions:**
   - Извлекается только объект `function` из каждого tool
   - Сохраняется структура parameters

3. **Трансформация tool_choice → function_call:**
   - `{"type": "function", "function": {"name": "get_current_weather"}}` → `{"name": "get_current_weather"}`

**Результирующий GigaChat payload:**

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "system",
      "content": "Ты полезный ассистент, который помогает пользователям с различными задачами."
    },
    {
      "role": "user",
      "content": "Привет! Можешь помочь мне с погодой в Москве?[Image: https://example.com/weather-map.jpg]"
    },
    {
      "role": "assistant",
      "content": "Конечно! Я помогу вам узнать погоду в Москве."
    },
    {
      "role": "user",
      "content": "Какая сейчас температура?"
    }
  ],
  "functions": [
    {
      "name": "get_current_weather",
      "description": "Получить текущую погоду в указанном городе",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "Город и страна, например 'Москва, Россия'"
          },
          "unit": {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "Единица измерения температуры"
          }
        },
        "required": ["location"]
      }
    },
    {
      "name": "get_weather_forecast",
      "description": "Получить прогноз погоды на несколько дней",
      "parameters": {
        "type": "object",
        "properties": {
          "location": {
            "type": "string",
            "description": "Город и страна"
          },
          "days": {
            "type": "integer",
            "description": "Количество дней для прогноза",
            "minimum": 1,
            "maximum": 7
          }
        },
        "required": ["location", "days"]
      }
    }
  ],
  "function_call": {
    "name": "get_current_weather"
  },
  "temperature": 0.7,
  "max_tokens": 1500,
  "top_p": 0.9,
  "stream": false
}
```

### 3. Другие примеры трансформаций

#### 3.1 Простой запрос без tools

**OpenAI:**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": "Расскажи анекдот"
    }
  ],
  "temperature": 0.8,
  "max_tokens": 200
}
```

**GigaChat (без изменений):**
```json
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": "Расскажи анекдот"
    }
  ],
  "temperature": 0.8,
  "max_tokens": 200,
  "stream": false
}
```

#### 3.2 Сложный content массив

**OpenAI:**
```json
{
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Что изображено на этой картинке? "
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...",
            "detail": "high"
          }
        },
        {
          "type": "text",
          "text": " Опиши детально."
        }
      ]
    }
  ]
}
```

**GigaChat:**
```json
{
  "model": "gpt-4-vision-preview",
  "messages": [
    {
      "role": "user",
      "content": "Что изображено на этой картинке? [Image: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ...] Опиши детально."
    }
  ],
  "stream": false
}
```

#### 3.3 Tool choice варианты

**OpenAI tool_choice: "auto":**
```json
{
  "tool_choice": "auto"
}
```
**GigaChat:**
```json
{
  "function_call": "auto"
}
```

**OpenAI tool_choice: "none":**
```json
{
  "tool_choice": "none"
}
```
**GigaChat:**
```json
{
  "function_call": "none"
}
```

---

## GigaChat → OpenAI: Исходящие ответы

### 1. Максимально полный GigaChat ответ

```json
{
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "function_call": {
          "name": "get_current_weather",
          "arguments": {
            "location": "Москва, Россия",
            "unit": "celsius"
          }
        }
      },
      "finish_reason": "function_call"
    }
  ],
  "created": 1703123456,
  "id": "giga-response-12345",
  "model": "GigaChat",
  "object": "chat.completion",
  "usage": {
    "completion_tokens": 25,
    "prompt_tokens": 150,
    "total_tokens": 175
  }
}
```

### 2. Трансформация в OpenAI формат

**Пошаговая трансформация:**

1. **Генерация OpenAI-совместимого ID:**
   - `"giga-response-12345"` → `"chatcmpl-a1b2c3d4-e5f6-7890-abcd-ef1234567890"`

2. **Трансформация function_call → tool_calls:**
   - Создается массив tool_calls с уникальным ID
   - Arguments сериализуются в JSON строку

3. **Адаптация finish_reason:**
   - `"function_call"` → `"tool_calls"`

4. **Стандартизация метаданных:**
   - Добавляется `system_fingerprint: null`
   - Обновляется timestamp

**Результирующий OpenAI ответ:**

```json
{
  "id": "chatcmpl-a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "object": "chat.completion",
  "created": 1703123456,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_a1b2c3d4e5f67890",
            "type": "function",
            "function": {
              "name": "get_current_weather",
              "arguments": "{\"location\": \"Москва, Россия\", \"unit\": \"celsius\"}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ],
  "usage": {
    "prompt_tokens": 150,
    "completion_tokens": 25,
    "total_tokens": 175
  },
  "system_fingerprint": null
}
```

### 3. Другие типы ответов

#### 3.1 Обычный текстовый ответ

**GigaChat:**
```json
{
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Привет! Я GigaChat, языковая модель от Сбера. Как дела? Чем могу помочь?",
        "function_call": null
      },
      "finish_reason": "stop"
    }
  ],
  "created": 1703123456,
  "id": "giga-response-67890",
  "model": "GigaChat-Pro",
  "usage": {
    "completion_tokens": 20,
    "prompt_tokens": 10,
    "total_tokens": 30
  }
}
```

**OpenAI:**
```json
{
  "id": "chatcmpl-b2c3d4e5-f6g7-8901-bcde-fg2345678901",
  "object": "chat.completion",
  "created": 1703123456,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Привет! Я GigaChat, языковая модель от Сбера. Как дела? Чем могу помочь?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30
  },
  "system_fingerprint": null
}
```

#### 3.2 Ответ с множественными function calls

**GigaChat (гипотетический):**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "function_call": {
          "name": "get_weather_and_forecast",
          "arguments": {
            "location": "Москва",
            "include_forecast": true,
            "days": 3
          }
        }
      }
    }
  ]
}
```

**OpenAI:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": null,
        "tool_calls": [
          {
            "id": "call_c3d4e5f6g7h89012",
            "type": "function",
            "function": {
              "name": "get_weather_and_forecast",
              "arguments": "{\"location\": \"Москва\", \"include_forecast\": true, \"days\": 3}"
            }
          }
        ]
      },
      "finish_reason": "tool_calls"
    }
  ]
}
```

---

## Специальные случаи

### 1. Обработка пустых или некорректных данных

#### 1.1 Пустой function_call

**GigaChat:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Извините, не могу выполнить функцию.",
        "function_call": {}
      }
    }
  ]
}
```

**OpenAI (function_call игнорируется):**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Извините, не могу выполнить функцию."
      },
      "finish_reason": "stop"
    }
  ]
}
```

#### 1.2 Отсутствие usage информации

**GigaChat:**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Ответ без usage"
      }
    }
  ],
  "usage": null
}
```

**OpenAI (добавляются нулевые значения):**
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Ответ без usage"
      }
    }
  ],
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0,
    "total_tokens": 0
  }
}
```

### 2. Сложные content структуры

#### 2.1 Вложенные объекты в content

**OpenAI:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Анализируй этот код: "
        },
        {
          "type": "text", 
          "text": "```python\ndef hello():\n    print('Hello, World!')\n```"
        },
        {
          "custom_field": "value",
          "text": " и объясни что он делает."
        }
      ]
    }
  ]
}
```

**GigaChat:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Анализируй этот код: ```python\ndef hello():\n    print('Hello, World!')\n``` и объясни что он делает."
    }
  ]
}
```

#### 2.2 Смешанные типы в content

**OpenAI:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": [
        "Простая строка",
        {
          "type": "text",
          "text": " и объект с текстом"
        },
        123,
        {
          "unknown_type": "data",
          "text": " финальный текст"
        }
      ]
    }
  ]
}
```

**GigaChat:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "Простая строка и объект с текстом123 финальный текст"
    }
  ]
}
```

---

## Streaming трансформации

### 1. OpenAI Streaming запрос

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Расскажи длинную историю"
    }
  ],
  "stream": true,
  "temperature": 0.7
}
```

### 2. GigaChat Streaming запрос (без изменений)

```json
{
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Расскажи длинную историю"
    }
  ],
  "stream": true,
  "temperature": 0.7
}
```

### 3. GigaChat Streaming ответы

**Chunk 1:**
```json
{
  "id": "giga-stream-12345",
  "object": "chat.completion.chunk",
  "created": 1703123456,
  "model": "GigaChat",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "Жила"
      },
      "finish_reason": null
    }
  ]
}
```

**Chunk 2:**
```json
{
  "id": "giga-stream-12345",
  "object": "chat.completion.chunk", 
  "created": 1703123456,
  "model": "GigaChat",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "-была"
      },
      "finish_reason": null
    }
  ]
}
```

**Final Chunk:**
```json
{
  "id": "giga-stream-12345",
  "object": "chat.completion.chunk",
  "created": 1703123456,
  "model": "GigaChat",
  "choices": [
    {
      "index": 0,
      "delta": {},
      "finish_reason": "stop"
    }
  ]
}
```

### 4. OpenAI Streaming ответы (трансформированные)

**Chunk 1:**
```json
{
  "id": "chatcmpl-d4e5f6g7-h8i9-0123-cdef-gh3456789012",
  "object": "chat.completion.chunk",
  "created": 1703123456,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "delta": {
        "role": "assistant",
        "content": "Жила"
      },
      "finish_reason": null
    }
  ],
  "system_fingerprint": null
}
```

**Chunk 2:**
```json
{
  "id": "chatcmpl-d4e5f6g7-h8i9-0123-cdef-gh3456789012",
  "object": "chat.completion.chunk",
  "created": 1703123456,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "-была"
      },
      "finish_reason": null
    }
  ],
  "system_fingerprint": null
}
```

**Final Chunk:**
```json
{
  "id": "chatcmpl-d4e5f6g7-h8i9-0123-cdef-gh3456789012",
  "object": "chat.completion.chunk",
  "created": 1703123456,
  "model": "gpt-4",
  "choices": [
    {
      "index": 0,
      "delta": {},
      "finish_reason": "stop"
    }
  ],
  "system_fingerprint": null
}
```

---

## Обработка ошибок

### 1. Ошибки авторизации

**GigaChat ошибка:**
```json
{
  "error": {
    "code": "UNAUTHORIZED",
    "message": "Invalid or expired token"
  }
}
```

**OpenAI формат:**
```json
{
  "error": {
    "message": "Invalid authentication credentials",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### 2. Ошибки модели

**GigaChat ошибка:**
```json
{
  "error": {
    "code": "MODEL_NOT_FOUND",
    "message": "Requested model is not available"
  }
}
```

**OpenAI формат:**
```json
{
  "error": {
    "message": "Model 'gigachat-unknown' not found",
    "type": "invalid_request_error", 
    "code": "model_not_found"
  }
}
```

### 3. Ошибки rate limiting

**GigaChat ошибка:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Too many requests"
  }
}
```

**OpenAI формат:**
```json
{
  "error": {
    "message": "Rate limit exceeded",
    "type": "rate_limit_error",
    "code": "rate_limit_exceeded"
  }
}
```

---

## Сводная таблица трансформаций

| OpenAI поле | GigaChat поле | Трансформация | Примечания |
|-------------|---------------|---------------|------------|
| `tools` | `functions` | Извлечение `function` объекта | Массив tools → массив functions |
| `tool_choice` | `function_call` | Упрощение структуры | `{"type": "function", "function": {"name": "X"}}` → `{"name": "X"}` |
| `messages[].content` (array) | `messages[].content` (string) | Конкатенация | Массив объектов → строка |
| `function_call` | `tool_calls` | Обертка в массив | Один объект → массив с ID |
| `finish_reason: "function_call"` | `finish_reason: "tool_calls"` | Переименование | Адаптация под OpenAI стандарт |
| ID генерация | ID генерация | UUID генерация | `chatcmpl-*` для OpenAI, `call_*` для tool_calls |

---

## Заключение

Данная документация покрывает все основные сценарии трансформации JSON payload между OpenAI и GigaChat API. Трансформер обеспечивает полную совместимость, позволяя использовать GigaChat через стандартный OpenAI интерфейс без изменения клиентского кода.

### Ключевые особенности:

1. **Двунаправленная трансформация** - поддержка как входящих запросов, так и исходящих ответов
2. **Сохранение функциональности** - все возможности OpenAI API доступны через GigaChat
3. **Обработка ошибок** - корректная трансформация ошибок в OpenAI формат
4. **Streaming поддержка** - полная совместимость с потоковыми ответами
5. **Безопасность** - валидация и обработка некорректных данных

Трансформер автоматически определяет тип запроса и применяет соответствующие трансформации, обеспечивая прозрачную работу с GigaChat API через привычный OpenAI интерфейс.
