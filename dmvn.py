import requests
from requests.exceptions import ReadTimeout, ConnectionError
import telegram
from dotenv import load_dotenv
import os
import sys

load_dotenv()


API_TOKEN = os.environ["API_TOKEN"]
TG_TOKEN = os.environ["TG_TOKEN"]

URL_LIST_LONG_POLLING = "https://dvmn.org/api/long_polling/"

bot = telegram.Bot(token=TG_TOKEN)

headers = {"Authorization": f"Token {API_TOKEN}"}
timestamp = None

if len(sys.argv) == 2:
    MY_CHAT_ID = sys.argv[1]
else:
    print(sys.argv)
    print(
        "Необходимо передать ровно 1 параметр: id чата в телеграм, для отправки сообщений"
    )
    sys.exit()

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
                chat_id=MY_CHAT_ID,
            )

        else:
            timestamp = data.get("timestamp_to_request")

    except ReadTimeout:
        print("Request timed out. Let's try again later.")
    except ConnectionError:
        print("Connection error occurred. Please check your internet connection.")
