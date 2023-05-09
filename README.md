# dvmn-chatbot

Чат-бот, присылающий уведомления в предоставленный телеграм id о проверке работ на сайте https://dvmn.org/

## Для запуска

* создать venv, установить зависимости из requirements.txt

```
python3 -m venv myenv
source venv/bin/activate
pip install -r requirements.txt
```

* создать .env файл, в котором указать API_TOKEN = API_TOKEN для доступа к сайту dvmn и TELEGRAM_TOKEN = TELEGRAM_TOKEN вашего ТГ-бота
```
API_TOKEN=your_apitoken_for_dvmn.org
TELEGRAM_TOKEN=token_of_your_tg_bot
```
* запустить скрипт notification_tg_bot.py с указанием аргумента - id получателя сообщений в телеграме:

```
python3 notification_tg_bot.py 123456789
```
* отправить работу на проверку - вернуть работу с проверки, увидеть у указанного ранее получателя сообщений полученное от бота сообщение вида:
```
Преподаватель проверил работу 'Отправляем уведомления о проверке работ'.                 
К сожалению, в работе нашлись ошибки.
URL проверенной работы: 
```