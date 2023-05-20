import requests
from requests.exceptions import ReadTimeout, ConnectionError
import telegram
from dotenv import load_dotenv
import os
import argparse
import time
import logging

URL_LIST_LONG_POLLING = "https://dvmn.org/api/long_polling/"


class TelegramLogsHandler(logging.Handler):
    def __init__(self, tg_bot, chat_id):
        super().__init__()
        self.chat_id = chat_id
        self.tg_bot = tg_bot

    def emit(self, record):
        log_entry = self.format(record)
        self.tg_bot.send_message(chat_id=self.chat_id, text=log_entry)


def main(bot):
    dvmn_api_token = os.environ["DVMN_API_TOKEN"]
    headers = {"Authorization": f"Token {dvmn_api_token}"}
    timestamp = None

    logger.info("Bot started")

    while True:
        params = {"timestamp": timestamp}

        try:
            response = requests.get(
                url=URL_LIST_LONG_POLLING, headers=headers, timeout=9, params=params
            )
            response.raise_for_status()

            attempts_data = response.json()
            status = attempts_data.get("status")

            if status == "found":
                timestamp = attempts_data.get("last_attempt_timestamp")

                attempt = attempts_data.get("new_attempts")[0]
                is_negative = attempt.get("is_negative")
                lesson_title = attempt.get("lesson_title")
                lesson_url = attempt.get("lesson_url")

                bot.send_message(
                    text=f"Преподаватель проверил работу '{lesson_title}'.\n"
                    + f"{'К сожалению, в работе нашлись ошибки.' if is_negative else 'Всё ОК, можно приступать к следующему уроку.'}\n"
                    + f"URL проверенной работы:\n {lesson_url}.",
                    chat_id=tg_chat_id,
                )

            else:
                timestamp = attempts_data.get("timestamp_to_request")

        except ReadTimeout:
            pass
        except ConnectionError:
            print("Connection error occurred. Please check your internet connection.")
            time.sleep(10)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Отправлять уведомления о проверке работ в предоставленный id телеграма"
    )
    parser.add_argument("tg_chat_id", help="Ваш chat_id в телеграме")
    args = parser.parse_args()

    tg_chat_id = args.tg_chat_id
    # tg_chat_id = 364129987

    load_dotenv()

    telegram_token = os.environ["TELEGRAM_TOKEN"]
    bot = telegram.Bot(token=telegram_token)

    logger = logging.getLogger("Logger")
    logger.setLevel(logging.INFO)  # TODO: change to WARNING
    logger.addHandler(TelegramLogsHandler(bot, tg_chat_id))

    main(bot=bot)
