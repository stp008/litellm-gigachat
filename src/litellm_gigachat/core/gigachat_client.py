import litellm
import logging
from .token_manager import get_gigachat_token
from ..callbacks.token_callback import setup_litellm_gigachat_integration

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Основная функция для демонстрации работы с GigaChat через LiteLLM"""
    
    # ── 1. Настройка интеграции с автоматическим обновлением токенов ──
    logger.info("Настройка интеграции GigaChat с LiteLLM...")
    setup_litellm_gigachat_integration()
    
    # ── 2. Получение актуального токена (автоматически обновляется) ──
    logger.info("Получение токена GigaChat...")
    token = get_gigachat_token()
    logger.info("Токен успешно получен")
    
    # ── 3. Вызов GigaChat через LiteLLM ──
    logger.info("Отправка запроса к GigaChat...")
    
    try:
        response = litellm.completion(
            model="openai/GigaChat",              # «openai/» говорит LiteLLM, что это OAI-совместимый бэкенд
            api_base="https://gigachat.devices.sberbank.ru/api/v1",
            api_key=token,                        # Токен будет автоматически обновлен callback'ом при необходимости
            messages=[{"role": "user", "content": "Привет, Giga! Расскажи кратко о себе."}],
        )
        
        logger.info("Ответ получен успешно")
        print("\n" + "="*50)
        print("ОТВЕТ GIGACHAT:")
        print("="*50)
        print(response.choices[0].message.content)
        print("="*50)
        
        # Информация об использовании токенов
        if hasattr(response, 'usage') and response.usage:
            print(f"\nИспользование токенов:")
            print(f"  Запрос: {response.usage.prompt_tokens}")
            print(f"  Ответ: {response.usage.completion_tokens}")
            print(f"  Всего: {response.usage.total_tokens}")
        
    except Exception as e:
        logger.error(f"Ошибка при вызове GigaChat: {e}")
        raise

def test_multiple_requests():
    """Тест множественных запросов для проверки автоматического обновления токенов"""
    
    logger.info("Тестирование множественных запросов...")
    setup_litellm_gigachat_integration()
    
    questions = [
        "Что такое искусственный интеллект?",
        "Расскажи о Python",
        "Какая погода в Москве?",
    ]
    
    for i, question in enumerate(questions, 1):
        logger.info(f"Запрос {i}/{len(questions)}: {question}")
        
        try:
            token = get_gigachat_token()  # Автоматически обновится при необходимости
            
            response = litellm.completion(
                model="openai/GigaChat",
                api_base="https://gigachat.devices.sberbank.ru/api/v1",
                api_key=token,
                messages=[{"role": "user", "content": question}],
            )
            
            print(f"\n--- Ответ {i} ---")
            print(response.choices[0].message.content[:200] + "..." if len(response.choices[0].message.content) > 200 else response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Ошибка в запросе {i}: {e}")

if __name__ == "__main__":
    # Запуск основной демонстрации
    main()
    
    # Раскомментируйте для тестирования множественных запросов
    # test_multiple_requests()
