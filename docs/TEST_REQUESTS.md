# Примеры запросов для тестирования GigaChat через LiteLLM

После запуска прокси-сервера (`python start_proxy.py`) вы можете тестировать API различными способами.

## 1. Тестирование через curl

### Базовый запрос
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

### Запрос с параметрами
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{
    "model": "gigachat-pro",
    "messages": [
      {"role": "user", "content": "Расскажи о машинном обучении"}
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
  }'
```

### Потоковый запрос
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{
    "model": "gigachat",
    "messages": [
      {"role": "user", "content": "Расскажи короткую историю"}
    ],
    "stream": true
  }'
```

### Диалог с контекстом
```bash
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{
    "model": "gigachat",
    "messages": [
      {"role": "user", "content": "Меня зовут Алексей"},
      {"role": "assistant", "content": "Приятно познакомиться, Алексей! Как дела?"},
      {"role": "user", "content": "Как меня зовут?"}
    ]
  }'
```

### Получение списка моделей
```bash
curl -X GET http://localhost:4000/v1/models \
  -H "Authorization: Bearer any-key"
```

## 2. Тестирование через Python (OpenAI SDK)

```python
import openai

# Настройка клиента
client = openai.OpenAI(
    base_url="http://localhost:4000",
    api_key="any-key"
)

# Простой запрос
response = client.chat.completions.create(
    model="gigachat",
    messages=[
        {"role": "user", "content": "Привет!"}
    ]
)
print(response.choices[0].message.content)

# Потоковый запрос
stream = client.chat.completions.create(
    model="gigachat",
    messages=[
        {"role": "user", "content": "Расскажи историю"}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="")
```

## 3. Тестирование через JavaScript/Node.js

```javascript
const OpenAI = require('openai');

const openai = new OpenAI({
  baseURL: 'http://localhost:4000',
  apiKey: 'any-key'
});

async function testGigaChat() {
  try {
    const response = await openai.chat.completions.create({
      model: 'gigachat',
      messages: [
        { role: 'user', content: 'Привет, GigaChat!' }
      ]
    });
    
    console.log(response.choices[0].message.content);
  } catch (error) {
    console.error('Ошибка:', error);
  }
}

testGigaChat();
```

## 4. Тестирование через httpie

```bash
# Установка httpie: pip install httpie

# Базовый запрос
http POST localhost:4000/v1/chat/completions \
  Authorization:"Bearer any-key" \
  model=gigachat \
  messages:='[{"role": "user", "content": "Привет!"}]'

# Запрос с параметрами
http POST localhost:4000/v1/chat/completions \
  Authorization:"Bearer any-key" \
  model=gigachat-pro \
  messages:='[{"role": "user", "content": "Что такое AI?"}]' \
  temperature:=0.8 \
  max_tokens:=200
```

## 5. Тестирование через Postman

### Настройка запроса в Postman:

1. **Method**: POST
2. **URL**: `http://localhost:4000/v1/chat/completions`
3. **Headers**:
   - `Content-Type: application/json`
   - `Authorization: Bearer any-key`
4. **Body** (raw JSON):
```json
{
  "model": "gigachat",
  "messages": [
    {"role": "user", "content": "Привет, GigaChat!"}
  ],
  "temperature": 0.7,
  "max_tokens": 500
}
```

## 6. Примеры ответов

### Успешный ответ
```json
{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "gigachat",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Привет! Я GigaChat, языковая модель от Сбера. Как дела?"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 15,
    "total_tokens": 25
  }
}
```

### Потоковый ответ
```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gigachat","choices":[{"index":0,"delta":{"content":"Привет"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gigachat","choices":[{"index":0,"delta":{"content":"!"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"gigachat","choices":[{"index":0,"delta":{},"finish_reason":"stop"}]}

data: [DONE]
```

## 7. Тестирование различных моделей

```bash
# GigaChat (базовая модель)
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{"model": "gigachat", "messages": [{"role": "user", "content": "Тест"}]}'

# GigaChat Pro
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{"model": "gigachat-pro", "messages": [{"role": "user", "content": "Тест"}]}'

# GigaChat Max
curl -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer any-key" \
  -d '{"model": "gigachat-max", "messages": [{"role": "user", "content": "Тест"}]}'
```

## 8. Обработка ошибок

### Ошибка авторизации (если токен истек)
```json
{
  "error": {
    "message": "Invalid authentication credentials",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}
```

### Ошибка модели
```json
{
  "error": {
    "message": "Model 'invalid-model' not found",
    "type": "invalid_request_error",
    "code": "model_not_found"
  }
}
```

## 9. Мониторинг и отладка

### Проверка статуса сервера
```bash
curl -X GET http://localhost:4000/health
```

### Получение информации о сервере
```bash
curl -X GET http://localhost:4000/v1/models
```

### Логи сервера
Логи отображаются в консоли при запуске `python start_proxy.py`

## 10. Нагрузочное тестирование

### Простой скрипт для нагрузочного тестирования
```bash
#!/bin/bash
for i in {1..10}; do
  echo "Запрос $i"
  curl -X POST http://localhost:4000/v1/chat/completions \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer any-key" \
    -d "{\"model\": \"gigachat\", \"messages\": [{\"role\": \"user\", \"content\": \"Тест $i\"}]}" \
    -w "Время ответа: %{time_total}s\n" \
    -s -o /dev/null
done
```

### Использование Apache Bench (ab)
```bash
# Установка: apt-get install apache2-utils (Ubuntu) или brew install httpie (macOS)

# Создание файла с данными запроса
echo '{"model": "gigachat", "messages": [{"role": "user", "content": "Тест"}]}' > request.json

# Нагрузочное тестирование
ab -n 100 -c 10 -T application/json -H "Authorization: Bearer any-key" -p request.json http://localhost:4000/v1/chat/completions
```

Эти примеры помогут вам протестировать все аспекты интеграции GigaChat с LiteLLM.
