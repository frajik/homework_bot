import os
from typing import Dict
import requests
import logging
import time
import telegram
from exeptions import StatusCodeError, ApiAnswerError, GetTokenFailed
from dotenv import load_dotenv
from http import HTTPStatus

load_dotenv()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
logger.addHandler(handler)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s - %(name)s"
)
handler.setFormatter(formatter)

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info("Сообщение отправлено успешно")
    except telegram.TelegramError as error:
        logger.error(f"Сообщение не отправлено:{error}")


def get_api_answer(current_timestamp):
    """Запрос к единственному эндпоинту API-сервиса."""
    timestamp = current_timestamp
    params = {'from_date': timestamp}
    try:
        homework = requests.get(ENDPOINT, headers=HEADERS, params=params)
        if homework.status_code != HTTPStatus.OK:
            raise StatusCodeError("Ожидаемый код ответа сервера не получен")
    except Exception:
        raise ApiAnswerError("Ошибка при запросе к серверу")
    return homework.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    try:
        hw = response["homeworks"][0]
    except KeyError as error:
        message = f"Нет ответа API по ключу 'homeworks'. Ошибка {error}"
        logger.error(message)
    if not isinstance(hw, list):
        message = "В ответе API домашки не в виде списков"
        logger.error(message)
        raise TypeError(message)
    return hw


def parse_status(homework):
    """Извлекает статус конкретной домашней работы."""
    if "homework_name" not in homework or "status" not in homework:
        raise KeyError("No homework_status_name or status in homework")
    if not isinstance(homework, Dict):
        raise TypeError("homework не является словарем")
    homework_name = homework["homework_name"]
    homework_status = homework["status"]
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
    except Exception:
        logger.error("Статус не определен")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_CHAT_ID and TELEGRAM_TOKEN:
        return True
    else:
        return False


def main():
    """Основная логика работы бота."""
    try:
        if check_tokens() is not True:
            raise GetTokenFailed
    except GetTokenFailed:
        logger.critical("Отсутствие обязательных переменных окружения")
        exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time() - RETRY_TIME)
    while True:
        try:
            response = get_api_answer(current_timestamp - RETRY_TIME)
            homework = check_response(response)
            if homework:
                bot.send_message(
                    TELEGRAM_CHAT_ID,
                    parse_status(homework)
                )

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(message)
            bot.send_message(
                TELEGRAM_CHAT_ID,
                message
            )
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
