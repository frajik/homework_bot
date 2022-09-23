import os
import sys
from typing import Dict
import requests
import logging
import time
import telegram
from exeptions import (
    StatusCodeError, ApiAnswerError, GetTokenFailed, SendMessageError
)
from dotenv import load_dotenv
from http import HTTPStatus


load_dotenv()

PRACTICUM_TOKEN = os.getenv("PRACTICUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    logger.debug("Отправляем сообщение в Telegram")
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.TelegramError as error:
        message = f"Ошибка при попытке отправить сообщение: {error}"
        raise SendMessageError(message)
    else:
        logger.info("Сообщение отправлено успешно")


def get_api_answer(current_timestamp):
    """Запрос к единственному эндпоинту API-сервиса."""
    logger.debug("Отправляем запрос к эндпоинту API-сервиса")
    timestamp = current_timestamp
    request_params = {
        "url": ENDPOINT,
        "params": {'from_date': timestamp},
        "headers": HEADERS
    }
    try:
        homework = requests.get(**request_params)
        if homework.status_code != HTTPStatus.OK:
            raise StatusCodeError("Ожидаемый код ответа сервера не получен")
    except Exception:
        raise ApiAnswerError("Ошибка при запросе к серверу")
    else:
        logger.info("Запрос к API выполнен успешно")
    return homework.json()


def check_response(response):
    """Проверяет ответ API на корректность."""
    logger.debug("Проверяем ответ API на корректность")
    try:
        homework = response["homeworks"]
    except KeyError as error:
        message = f"Нет ответа API по ключу 'homeworks'. Ошибка {error}"
        raise ApiAnswerError(message)
    if not isinstance(homework, list):
        message = "В ответе API домашки не в виде списков"
        logger.error(message)
        raise TypeError(message)
    else:
        logger.info("Ответ API корректен")
    return homework


def parse_status(homework):
    """Извлекает статус конкретной домашней работы."""
    if homework is None:
        logger.error("Данные с домашней работой не найдены")
        raise KeyError("Домашняя работа отсутствует")
    logger.debug("Получаем статус домашней работы")
    if "homework_name" not in homework or "status" not in homework:
        raise KeyError("No homework_status_name or status in homework")
    if not isinstance(homework, Dict):
        raise TypeError("homework не является словарем")
    homework_name = homework["homework_name"]
    homework_status = homework["status"]
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except Exception:
        logger.error("Статус не определен")
    else:
        logger.info("Статус домашней работы получен")
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens():
    """Проверяет доступность переменных окружения."""
    logger.debug("Проверяем доступность переменных окружения")
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
    current_timestamp = 0
    old_message = ""
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homework = check_response(response)
            if homework:
                message = parse_status(homework[0])
                if message != old_message:
                    send_message(bot, message)
                    old_message = message
                else:
                    logger.debug("Статус проверки не изменился")

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logger.critical(message)
            send_message(
                bot,
                message
            )
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    handler = logging.StreamHandler(sys.stdout)
    handler_logs = logging.FileHandler("my_logs.log")
    logger.addHandler(handler)
    logger.addHandler(handler_logs)
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s - %(name)s - %(lineno)s"
    )
    handler.setFormatter(formatter)
    handler_logs.setFormatter(formatter)
    main()
