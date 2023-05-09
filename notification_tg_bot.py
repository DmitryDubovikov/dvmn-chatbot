import requests
from requests.exceptions import ReadTimeout, ConnectionError
import telegram
from dotenv import load_dotenv
import os
import argparse
import time


def main():
    parser = argparse.ArgumentParser(
        description="Отправлять уведомления о проверке работ в предоставленный id телеграма"
    )
    parser.add_argument("tg_chat_id", help="Ваш chat_id в телеграме")
    args = parser.parse_args()

    load_dotenv()

    API_TOKEN = os.environ["API_TOKEN"]
    TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]

    URL_LIST_LONG_POLLING = "https://dvmn.org/api/long_polling/"

    bot = telegram.Bot(token=TELEGRAM_TOKEN)

    headers = {"Authorization": f"Token {API_TOKEN}"}
    timestamp = None

    while True:
        params = {"timestamp": timestamp}

        try:
            response = requests.get(
                url=URL_LIST_LONG_POLLING, headers=headers, timeout=9, params=params
            )
            response.raise_for_status()

            response_json = response.json()
            status = response_json.get("status")

            if status == "found":
                timestamp = response_json.get("last_attempt_timestamp")

                attempt = response_json.get("new_attempts")[0]
                is_negative = attempt.get("is_negative")
                lesson_title = attempt.get("lesson_title")
                lesson_url = attempt.get("lesson_url")

                bot.send_message(
                    text=f"""
                    Преподаватель проверил работу '{lesson_title}'.                 
                    {'К сожалению, в работе нашлись ошибки.' if is_negative else 'Всё ОК, можно приступать к следующему уроку.'}
                    URL проверенной работы: {lesson_url}.""",
                    chat_id=args.tg_chat_id,
                )

            else:
                timestamp = response_json.get("timestamp_to_request")

        except ReadTimeout:
            pass
        except ConnectionError:
            print("Connection error occurred. Please check your internet connection.")
            time.sleep(10)


if __name__ == "__main__":
    main()
