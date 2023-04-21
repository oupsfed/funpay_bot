import logging
from http import HTTPStatus

import requests
from bs4 import BeautifulSoup as bs


def make_int(text: str):
    text = text.replace(' ', '')
    text = text.replace('₽', '')
    text = text.replace('к', '')
    return int(text)


def make_float(text: str):
    text = text.replace(' ', '')
    text = text.replace('₽', '')
    text = text.replace('к', '')
    return float(text)


def make_bool(text):
    if text:
        return True
    return False


parse_classes = [
    {
        'name': 'server',
        'block': 'div',
        'class': 'tc-server'
    },
    {
        'name': 'seller',
        'block': 'div',
        'class': 'media-user-name'
    },
    {
        'name': 'item_name',
        'block': 'div',
        'class': 'tc-desc-text'
    },
    {
        'name': 'amount',
        'block': 'div',
        'class': 'tc-amount',
        'func': make_int
    },
    {
        'name': 'price',
        'block': 'div',
        'class': 'tc-price',
        'func': make_float
    },
    {
        'name': 'online',
        'block': 'div',
        'class': 'online',
        'func': make_bool
    }
]


def parse_info(link):
    answer = requests.get(link)
    if answer.status_code == HTTPStatus.OK:
        logging.debug('Ответ от сайта получен')
    soup = bs(answer.text, "html.parser")
    items = soup.find_all('a', class_='tc-item')
    data = []
    if items:
        logging.debug('Данные отсортированы')
    for item in items:
        item_data = {}
        for parse_classe in parse_classes:
            item_data[parse_classe['name']] = None
            info = item.find(parse_classe['block'],
                             class_=parse_classe['class'])
            if info:
                info = info.text.strip()
            if 'func' in parse_classe:
                info = parse_classe['func'](info)
            item_data[parse_classe['name']] = info
        item_data['link'] = item['href']
        data.append(item_data)
    return data
