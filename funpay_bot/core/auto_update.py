import time

import requests

HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}

while True:
    try:
        answer = requests.post(
            'http://127.0.0.1:8000/api/items/update/',
            headers=HEADERS
        )
        print(answer.json())
    except Exception as error:
        message = f'Сбой в работе программы: {error}'
        print(message)
    finally:
        time.sleep(60)
