import logging
import requests
from config.settings import TELEGRAM_URL, TELEGRAM_BOT_URL

logger = logging.getLogger(__name__)


def send_tg_reminder(chat_id, message):
    """Отправляет напоминание в Telegram."""
    params = {
        'text': message,
        'chat_id': chat_id
    }
    
    url = f"{TELEGRAM_URL}{TELEGRAM_BOT_URL}/sendMessage"
    logger.info(f"Отправка сообщения в Telegram: chat_id={chat_id}, url={url}")
    
    try:
        response = requests.get(url, params=params, timeout=10)
        logger.info(f"Ответ от Telegram API: статус={response.status_code}")
        
        response.raise_for_status()

        result = response.json()
        logger.info(f"Результат от Telegram API: {result}")
        
        if not result.get('ok'):
            error_msg = f"Telegram API вернул ошибку: {result.get('description', 'Unknown error')}"
            logger.error(error_msg)
            raise Exception(error_msg)
        
        return result
    except requests.RequestException as e:
        logger.error(f"Ошибка при запросе к Telegram API: {str(e)}", exc_info=True)
        raise
