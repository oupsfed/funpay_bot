import asyncio
import json
import logging
import os
from http import HTTPStatus
from sys import stdout

import requests
import telegram
from dotenv import load_dotenv
from rest_framework import status
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()

token = os.getenv('TOKEN')
HEADERS = {'Content-type': 'application/json',
           'Content-Encoding': 'utf-8'}

SHORT_NAME = {
    'a': 'action',
    'l': 'lot_id',
    'g': 'game_id',
    'i': 'item_id',
    's': 'server_id',
    'o': 'is_online',
    'p': 'page',
    'pp': 'previous_page',
    'np': 'next_page',
    'u': 'chat_id'
}

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(stdout)
log_format = '%(asctime)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt=log_format)
handler.setFormatter(formatter)

logger.addHandler(handler)

URL = 'http://127.0.0.1:8000/api/'


def check_permission(chat_id):
    link = f'{URL}users/{chat_id}'
    answer = requests.get(link, headers=HEADERS)
    user = answer.json()
    return user['is_staff']


def wake_up(update, context):
    chat = update.effective_chat
    link = f'{URL}users/{chat.id}/'
    answer = requests.get(link, headers=HEADERS)
    if answer.status_code == status.HTTP_404_NOT_FOUND:
        data = {
            'first_name': chat.first_name,
            'last_name': chat.last_name,
            'telegram_chat_id': chat.id,
            'username': chat.username
        }
        answer = requests.post(
            f'{URL}users/',
            data=json.dumps(data),
            headers=HEADERS
        )
        response = answer.json()
        if answer.status_code != HTTPStatus.CREATED:
            text = (f'Произошла ошибка при добавлении {chat.username}'
                    f' в БД {response}')
        else:
            text = f'Добавлен новый пользователь {chat.username} в БД'
        logger.error(text)
    message = '''
<b>Данный бот находится в состоянии ЗБТ!</b>
Если хотите следить за информацией не блокируйте его.
И возможно скоро Вы получите доступ к ЗБТ.'''
    try:
        buttons = ReplyKeyboardMarkup([
            ['Избранные Товары', 'Поиск Товара'],
            ['Данные по подписке']
        ], resize_keyboard=True)
        context.bot.send_message(
            chat_id=chat.id,
            text=message,
            parse_mode='HTML',
            reply_markup=buttons
        )
        text = f'Сообщение было отправлено пользователю {chat.username}'
        logger.debug(text)
    except telegram.TelegramError:
        text = f'Ошибка при отправке сообщения пользователю: {chat.username}'
        logger.error(text)


def subscribe_info(update, context):
    chat = update.effective_chat
    if check_permission(chat.id):
        link = f'{URL}users/{chat.id}'
        answer = requests.get(link, headers=HEADERS)
        user = answer.json()
        message = f'Подписка заканчивается {user["subscribe_time"]}'
        button = [
            [InlineKeyboardButton('Продлить подписку', url=f'{URL}')]
        ]
        reply_markup = InlineKeyboardMarkup(button)
        update.message.reply_text(message, reply_markup=reply_markup)


def favorite_items(update, context):
    chat = update.effective_chat
    buttons = []
    if check_permission(chat.id):
        message = 'Ваши избранные товары:'
        link = f'{URL}following/?user__telegram_chat_id={chat.id}'
        answer = requests.get(link, headers=HEADERS)
        items = answer.json()
        items = items['results']

        for item in items:
            buttons.append(
                [InlineKeyboardButton(f'{item["server"]["name"]}',
                                      callback_data=f'a-show,'
                                                    f'i-{item["id"]},')]
            )
        buttons.append([
            InlineKeyboardButton('Добавить Товар',
                                 callback_data='a-add_favorite,')
        ])
        reply_markup = InlineKeyboardMarkup(buttons)
        update.message.reply_text(message, reply_markup=reply_markup)


def convert_to_list(data):
    data = data.split(',')
    converted_data = {}
    print(data)
    for item in data:
        if '-' in item:
            item = item.split('-')
            print(SHORT_NAME[item[0]])
            item_name = SHORT_NAME[item[0]]
            item_value = item[1]
            converted_data[item_name] = item_value
    return converted_data


def show_item(update):
    query = update.callback_query
    data = convert_to_list(query.data)
    link = f'{URL}following/{data["item_id"]}'
    answer = requests.get(link, headers=HEADERS)
    item = answer.json()
    is_online_sellers = 'Нет'
    if item['monitoring_online_sellers']:
        is_online_sellers = 'Да'
    message = (f"Игра: <b>{item['lot']['game']}</b>\n"
               f"Сервер: <b>{item['server']['name']}</b>\n"
               f"Товар: <b>{item['lot']['name']}</b>\n"
               f"Ссылка: <b>{item['lot']['link']}</b>\n"
               f"<b>На данный момент цена: {item['price']}</b> ₽")

    buttons = [
        [InlineKeyboardButton(
            f'Только онлайн продавцы: {is_online_sellers}',
            callback_data=(f'a-monitoring,'
                           f'i-{item["id"]},'
                           f'o-{item["monitoring_online_sellers"]}'))],
        [InlineKeyboardButton(
            'Удалить',
            callback_data=f'a-delete,'
                          f'i-{item["id"]}')],
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(text=message,
                            parse_mode='HTML',
                            reply_markup=reply_markup)


def delete_item(update):
    query = update.callback_query
    data = convert_to_list(query.data)
    link = f'{URL}following/{data["item_id"]}'
    requests.delete(link, headers=HEADERS)
    message = 'Избранный товар успешно удален!'
    query.edit_message_text(text=message, parse_mode='HTML')


def add_favorite_item_lot(update):
    query = update.callback_query
    link = f'{URL}lots'
    answer = requests.get(link, headers=HEADERS)
    lots = answer.json()['results']
    print(lots)
    buttons = []
    for lot in lots:
        buttons.append(
            [InlineKeyboardButton(
                f'{lot["game"]} {lot["name"]}',
                callback_data=f'a-add_server,'
                              f'i-{lot["id"]},'
                              f'g-{lot["game_id"]}')]
        )
    message = 'Выберите Игру:'
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


def add_favorite_item_server(update):
    query = update.callback_query
    data = convert_to_list(query.data)
    link = f'{URL}servers/?game__id={data["game_id"]}'
    if 'page' in data:
        link = f'{URL}servers/?game__id={data["game_id"]}&page={data["page"]}'
        print(link)
    answer = requests.get(link, headers=HEADERS)
    servers = answer.json()['results']
    next_page = answer.json()['next']
    previous_page = answer.json()['previous']
    print(answer.json()['next'], answer.json()['previous'])

    buttons = []
    for server in servers:
        buttons.append(
            [InlineKeyboardButton(
                f'{server["name"]}',
                callback_data=f'a-add_lot,'
                              f'i-{data["item_id"]},'
                              f's-{server["id"]}'
            )]
        )
    if previous_page:
        previous_page = previous_page.split('page=')
        if len(previous_page) == 1:
            previous_page = ['page', 1]
        previous_page = previous_page[1]
        buttons.append(
            [InlineKeyboardButton(
                'Предыдущие',
                callback_data=(f'a-add_server,'
                               f'i-{data["item_id"]},'
                               f'g-{data["game_id"]},'
                               f'p-{previous_page}'))]
        )
    if next_page:
        next_page = next_page.split('page=')
        next_page = next_page[1]
        buttons.append(
            [InlineKeyboardButton(
                'Следующие',
                callback_data=(f'a-add_server,'
                               f'i-{data["item_id"]},'
                               f'g-{data["game_id"]},'
                               f'p-{next_page}'))]
        )
    message = 'Выберите сервер:'
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


def add_favorite_item_online_sellers(update):
    query = update.callback_query
    data = convert_to_list(query.data)
    buttons = [
        [InlineKeyboardButton(
            'Да',
            callback_data=f'a-add_favorite_done,'
                          f'i-{data["item_id"]},'
                          f's-{data["server_id"]},'
                          f'o-1')],
        [InlineKeyboardButton(
            'Нет',
            callback_data=f'a-add_favorite_done,'
                          f'i-{data["item_id"]},'
                          f's-{data["server_id"]},'
                          f'o-')],
    ]

    message = 'Следить только за онлайн продавцами?:'
    reply_markup = InlineKeyboardMarkup(buttons)
    query.edit_message_text(
        text=message,
        parse_mode='HTML',
        reply_markup=reply_markup
    )


def add_favorite_item_send_data(update):
    query = update.callback_query
    data = convert_to_list(query.data)
    new_follow = {
        'lot': int(data['item_id']),
        'user': update.effective_chat.id,
        'server': int(data['server_id']),
    }
    print(new_follow)
    link = f'{URL}following/'
    answer = requests.post(link, data=json.dumps(new_follow), headers=HEADERS)
    response = answer.json()
    if answer.status_code != HTTPStatus.CREATED:
        text = ('Произошла ошибка при добавлении '
                f'избранного предмета в БД: {response}')
        message = 'Произошла ошибка при добавлении избранного предмета!'
    else:
        text = f'Добавлен новый избранный предмет {new_follow} в БД'
        message = 'Избранный предмет успешно добавлен!'
    logger.error(text)
    query.edit_message_text(text=message, parse_mode='HTML')


def change_favorite_item_monitoring(update):
    query = update.callback_query
    data = convert_to_list(query.data)
    link = f'{URL}following/{data["item_id"]}/'
    is_monitoring = True
    if data["is_online"] == 'True':
        is_monitoring = False
    data = {
        'monitoring_online_sellers': is_monitoring
    }
    requests.patch(link, data=json.dumps(data), headers=HEADERS)
    message = 'Действие прошло успешно!'
    query.edit_message_text(text=message, parse_mode='HTML')


def inline_buttons(update, _):
    query = update.callback_query
    data = convert_to_list(query.data)

    actions = {
        'show': show_item,
        'delete': delete_item,
        'add_favorite': add_favorite_item_lot,
        'add_server': add_favorite_item_server,
        'add_lot': add_favorite_item_online_sellers,
        'add_favorite_done': add_favorite_item_send_data,
        'monitoring': change_favorite_item_monitoring
    }
    actions[data['action']](update)


async def main():
    """Основная логика работы бота."""
    updater = Updater(token=token)
    updater.dispatcher.add_handler(
        CommandHandler('start', wake_up)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Данные по подписке'), subscribe_info)
    )
    updater.dispatcher.add_handler(
        MessageHandler(Filters.text('Избранные Товары'), favorite_items)
    )
    updater.dispatcher.add_handler(
        CallbackQueryHandler(inline_buttons)
    )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    asyncio.run(main())
