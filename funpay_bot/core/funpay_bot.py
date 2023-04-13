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
                                      callback_data=f'show-{item["id"]}')]
            )
        buttons.append([
            InlineKeyboardButton('Добавить Товар',
                                 callback_data='add_favorite-')
        ])
        reply_markup = InlineKeyboardMarkup(buttons)
        update.message.reply_text(message, reply_markup=reply_markup)


def button(update, _):
    query = update.callback_query
    variant = query.data.split('-')
    print(variant)
    action = variant[0]
    item_id = variant[1]
    if action == 'show':
        link = f'{URL}following/{item_id}'
        answer = requests.get(link, headers=HEADERS)
        query.answer()
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
                callback_data=(f'monitoring-{item["id"]}-'
                               f'{item["monitoring_online_sellers"]}'))],
            [InlineKeyboardButton(
                'Удалить',
                callback_data=f'delete-{item["id"]}')],
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(text=message,
                                parse_mode='HTML',
                                reply_markup=reply_markup)
    elif action == 'delete':
        link = f'{URL}following/{item_id}'
        requests.delete(link, headers=HEADERS)
        message = 'Избранный товар успешно удален!'
        query.edit_message_text(text=message, parse_mode='HTML')
    elif action == 'add_favorite':
        link = f'{URL}lots'
        answer = requests.get(link, headers=HEADERS)
        query.answer()
        lots = answer.json()['results']
        print(lots)
        buttons = []
        for lot in lots:
            buttons.append(
                [InlineKeyboardButton(
                    f'{lot["game"]} {lot["name"]}',
                    callback_data=f'add_server-{lot["id"]}-{lot["game_id"]}')]
            )
        message = 'Выберите Игру:'
        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    elif action == 'add_server':
        game_id = variant[2]
        link = f'{URL}servers/?game__id={game_id}'
        if 'page' in variant:
            link = f'{URL}servers/?game__id={game_id}&page={variant[4]}'
            print(link)
        answer = requests.get(link, headers=HEADERS)
        query.answer()
        servers = answer.json()['results']
        next_page = answer.json()['next']
        previous_page = answer.json()['previous']
        print(answer.json()['next'], answer.json()['previous'])

        buttons = []
        for server in servers:
            buttons.append(
                [InlineKeyboardButton(
                    f'{server["name"]}',
                    callback_data=f'add_lot-{item_id}-{server["id"]}')]
            )
        if previous_page:
            previous_page = previous_page.split('page=')
            if len(previous_page) == 1:
                previous_page = ['page', 1]
            previous_page = previous_page[1]
            buttons.append(
                [InlineKeyboardButton(
                    'Предыдущие',
                    callback_data=(f'add_server-{item_id}-'
                                   f'{game_id}-'
                                   f'page-{previous_page}'))]
            )
        if next_page:
            next_page = next_page.split('page=')
            next_page = next_page[1]
            buttons.append(
                [InlineKeyboardButton(
                    'Следующие',
                    callback_data=(f'add_server-{item_id}-'
                                   f'{game_id}-'
                                   f'page-{next_page}'))])
        message = 'Выберите сервер:'
        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        print(update.callback_query)
    elif action == 'add_lot':
        server_id = variant[2]
        buttons = [
            [InlineKeyboardButton(
                'Да',
                callback_data=f'add_favorite_done-{item_id}-{server_id}-1')],
            [InlineKeyboardButton(
                'Нет',
                callback_data=f'add_favorite_done-{item_id}-{server_id}-')],
        ]

        message = 'Следить только за онлайн продавцами?:'
        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
    elif action == 'add_favorite_done':
        server_id = variant[2]
        user = update.effective_chat.id
        data = {
            'lot': int(item_id),
            'user': user,
            'server': int(server_id),
        }
        link = f'{URL}following/'
        answer = requests.post(link, data=json.dumps(data), headers=HEADERS)
        response = answer.json()
        if answer.status_code != HTTPStatus.CREATED:
            text = ('Произошла ошибка при добавлении '
                    f'избранного предмета в БД: {response}')
            message = 'Произошла ошибка при добавлении избранного предмета!'
        else:
            text = f'Добавлен новый избранный предмет {data} в БД'
            message = 'Избранный предмет успешно добавлен!'
        logger.error(text)
        query.edit_message_text(text=message, parse_mode='HTML')
    elif action == 'monitoring':
        link = f'{URL}following/{item_id}/'
        is_monitoring = True
        if variant[2] == 'True':
            is_monitoring = False
        data = {
            'monitoring_online_sellers': is_monitoring
        }
        answer = requests.patch(link, data=json.dumps(data), headers=HEADERS)
        message = 'Действие прошло успешно!'
        query.edit_message_text(text=message, parse_mode='HTML')


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
        CallbackQueryHandler(button)
    )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    asyncio.run(main())
