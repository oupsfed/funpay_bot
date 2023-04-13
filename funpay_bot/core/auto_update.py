import datetime
import time

import requests

HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}

while True:
    now = datetime.datetime.now()
    now = now.strftime("%d.%m.%Y %H:%M:%S")
    try:
        answer = requests.post(
            'http://127.0.0.1:8000/api/items/update/',
            headers=HEADERS
        )
        print(f'{now}: {answer.json()}')
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        print(f'{now}: {message}')
    finally:
        time.sleep(60)
