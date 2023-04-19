import json

import requests
from requests import Response

URL = 'http://127.0.0.1:8000/api/'
HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}


def get_api_answer(endpoint: str,
                   params=None) -> Response:
    """
    Делает GET запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    params (dict) : параметры запроса

            Returns:
                    answer (dict): Информация с API-сервиса
    """
    endpoint = f'{URL}{endpoint}'
    answer = requests.get(
        url=endpoint,
        headers=HEADERS,
        params=params
    )
    return answer


def post_api_answer(endpoint: str,
                    data: dict) -> Response:
    """
    Делает POST запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа
                    data (dict): данные для отправки на API

            Returns:
                    homework (dict): Информация с API-сервиса в формате JSON
    """
    endpoint = f'{URL}{endpoint}'
    data = json.dumps(data)
    answer = requests.post(
        url=endpoint,
        data=data,
        headers=HEADERS
    )
    return answer


def delete_api_answer(endpoint: str) -> Response:
    """
    Делает GET запрос к эндпоинту API-сервиса.

            Parameters:
                    endpoint (str) : точка доступа

            Returns:
                    answer (dict): Информация с API-сервиса
    """
    endpoint = f'{URL}{endpoint}'
    answer = requests.delete(
        url=endpoint,
        headers=HEADERS,
    )
    return answer


def check_permissions(user_id: int) -> bool:
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['is_staff']
