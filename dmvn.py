import requests
from requests.exceptions import ReadTimeout, ConnectionError
import telegram
from dotenv import load_dotenv
import os
import argparse

parser = argparse.ArgumentParser(
    description="Отправлять уведомления о проверке работ в предоставленный id телеграма"
)
parser.add_argument("chat_id", help="Ваш chat_id в телеграме")
args = parser.parse_args()

load_dotenv()

API_TOKEN = os.environ["API_TOKEN"]
TG_TOKEN = os.environ["TG_TOKEN"]

URL_LIST_LONG_POLLING = "https://dvmn.org/api/long_polling/"

bot = telegram.Bot(token=TG_TOKEN)

headers = {"Authorization": f"Token {API_TOKEN}"}
timestamp = None


while True:
    params = {"timestamp": timestamp}

    try:
        response = requests.get(
            url=URL_LIST_LONG_POLLING, headers=headers, timeout=90, params=params
        )
        response.raise_for_status()

        data = response.json()
        status = data.get("status")

        if status == "found":
            timestamp = data.get("last_attempt_timestamp")

            attempt = data.get("new_attempts")[0]
            is_negative = attempt.get("is_negative")
            lesson_title = attempt.get("lesson_title")
            lesson_url = attempt.get("lesson_url")

            bot.send_message(
                text=f"""
                Преподаватель проверил работу '{lesson_title}'.                 
                {'К сожалению, в работе нашлись ошибки.' if is_negative else 'Всё ОК, можно приступать к следующему уроку.'}
                URL проверенной работы: {lesson_url}.""",
                chat_id=args.chat_id,
            )

        else:
            timestamp = data.get("timestamp_to_request")

    except ReadTimeout:
        print("Request timed out. Let's try again later.")
    except ConnectionError:
        print("Connection error occurred. Please check your internet connection.")
