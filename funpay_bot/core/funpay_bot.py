import asyncio
import json
import logging
import os
from http import HTTPStatus
from json import JSONDecodeError
from logging.handlers import RotatingFileHandler

import requests
import telegram
from dotenv import load_dotenv
from requests import Response
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      ReplyKeyboardMarkup)
from telegram.ext import (CallbackQueryHandler, CommandHandler, Filters,
                          MessageHandler, Updater)

load_dotenv()

token = os.getenv('TOKEN')
admin = os.getenv('ADMIN_CHAT_ID')
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

logging.basicConfig(
    level=logging.DEBUG,
    handlers=[logging.FileHandler(filename="./log_records.log",
                                  encoding='utf-8', mode='a+')],
    format='%(asctime)s - %(levelname)s - %(message)s',

)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(
    'my_logger.log',
    maxBytes=50000000,
    backupCount=5,
    encoding='UTF-8'
)
log_format = '%(asctime)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(fmt=log_format)
handler.setFormatter(formatter)

logger.addHandler(handler)

URL = 'http://127.0.0.1:8000/api/'


def check_permission(chat_id):
    answer = get_api_answer(f'users/{chat_id}')
    user = answer.json()
    if not user['is_staff']:
        message = 'Недостаточно прав для просмотра данного раздела'
        send_message(telegram.Bot(token), chat_id, message)
        logger.debug(f'У {chat_id} {message}')
    return user['is_staff']


def send_message(bot: telegram.Bot,
                 chat_id: int,
                 message: str) -> None:
    """
    Отправляет сообщение в сообщение в Telegram чат.

            Parameters:
                    bot (telegram.Bot): Объект класса telegram.Bot
                    chat_id (int): Кому отправить сообщение
                    message (str): Сообщение

            Returns:
                    None
    """
    buttons = ReplyKeyboardMarkup([
        ['Избранные Товары', 'Поиск Товара'],
        ['О проекте', 'Данные по подписке']
    ], resize_keyboard=True)
    try:
        bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML',
            reply_markup=buttons
        )
        logger.debug(
            (f'Сообщение было отправлено в '
             f'Telegram-чат пользователю: {chat_id}')
        )
    except telegram.TelegramError:
        logger.error(
            (f'Ошибка при отправке сообщения в '
             f'Telegram-чат пользователю: {chat_id}')
        )


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

    try:
        answer = requests.get(
            url=endpoint,
            headers=HEADERS,
            params=params
        )
        if answer.status_code != HTTPStatus.OK:
            message = f'Эндпоинт {endpoint} не доступен!'
            logger.error(message)
            send_message(telegram.Bot(token),
                         admin,
                         message)
            raise TypeError(message)
        text = f'Запрос к эндпоинту {endpoint} прошел успешно!'
        logger.debug(text)
        return answer
    except JSONDecodeError as error:
        message = f'Ошибка при обработке json: {error}'
        logger.error(message)
        send_message(telegram.Bot(token),
                     admin,
                     message)
    except requests.RequestException as error:
        message = f'Ошибка при запросе к API: {error}'
        logger.error(message)
        send_message(telegram.Bot(token),
                     admin,
                     message)


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
    try:
        answer = requests.post(
            url=endpoint,
            data=data,
            headers=HEADERS
        )
        if answer.status_code != HTTPStatus.CREATED:
            message = (f'Произошла ошибка при добавлении данных в базу '
                       f'Отправленные данные: {data}'
                       f'Ошибка: Response')
            logger.error(message)
            send_message(telegram.Bot(token),
                         admin,
                         message)
        text = f'Добавлена новая запись в базу данных: {data}'
        logger.debug(text)
        return answer
    except JSONDecodeError as error:
        message = f'Ошибка при обработке json: {error}'
        logger.error(message)
        send_message(telegram.Bot(token),
                     admin,
                     message)
    except requests.RequestException as error:
        message = f'Ошибка при запросе к API: {error}'
        logger.error(message)
        send_message(telegram.Bot(token),
                     admin,
                     message)


def wake_up(update, context):
    chat = update.effective_chat
    logger.debug((f'Новый пользователь запустил бота '
                  f'{chat.username} - {chat.id}'))

    answer = get_api_answer('users/',
                            params={
                                'telegram_chat_id': chat.id
                            })
    if answer.json()['count'] == 0:
        data = {
            'first_name': chat.first_name,
            'last_name': chat.last_name,
            'telegram_chat_id': chat.id,
            'username': chat.username
        }
        post_api_answer('users/', data)
    message = ('<b>Данный бот находится в состоянии ЗБТ!</b>\n'
               'Если хотите следить за информацией не блокируйте его.\n'
               'И возможно скоро Вы получите доступ к ЗБТ.')
    send_message(context.bot, chat.id, message)


def information(update, context):
    message = 'Информация о проекте!'
    update.message.reply_text(message)


def subscribe_info(update, context):
    chat = update.effective_chat
    if not check_permission(chat.id):
        return 'Access Denied'
    answer = get_api_answer(f'users/{chat.id}/')
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
        logger.debug(f'{chat.id} успешно зашел в избранные товары')
        message = 'Ваши избранные товары:'
        answer = get_api_answer('following/',
                                params={
                                    'user__telegram_chat_id': chat.id
                                })
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
    for item in data:
        if '-' in item:
            item = item.split('-')
            item_name = SHORT_NAME[item[0]]
            item_value = item[1]
            converted_data[item_name] = item_value
    text = f'Конвертированы данные {data} в {converted_data}'
    logger.debug(text)
    return converted_data


def show_item(update, data):
    query = update.callback_query
    answer = get_api_answer(f'following/{data["item_id"]}/')
    item = answer.json()
    is_online_sellers = 'Нет'
    if item['monitoring_online_sellers']:
        is_online_sellers = 'Да'
    logger.debug(f'{update.effective_chat.id} просматривает товар {item}')
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


def delete_item(update, data):
    query = update.callback_query
    link = f'{URL}following/{data["item_id"]}'
    answer = requests.delete(link, headers=HEADERS)
    if answer.status_code == HTTPStatus.NO_CONTENT:
        message = 'Избранный товар успешно удален!'
        logger.debug(f'{update.effective_chat.id} удалил избранный товар')
    else:
        message = 'Произошла ошибка при удалении товара!'
        logger.error(f'{message} {answer.json()}')
    query.edit_message_text(text=message, parse_mode='HTML')


def add_favorite_item_lot(update, data):
    query = update.callback_query
    answer = get_api_answer('lots')
    lots = answer.json()['results']
    logger.debug(f'{update.effective_chat.id} добавляет '
                 f'новый избранный товар')
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


def add_favorite_item_server(update, data):
    query = update.callback_query
    params = {
        'game__id': data['game_id']
    }
    if 'page' in data:
        params['page'] = data['page']
    answer = get_api_answer('servers/',
                            params=params)
    logger.debug(f'{update.effective_chat.id} выбирает сервер '
                 f'для игры {data["game_id"]}')
    servers = answer.json()['results']
    next_page = answer.json()['next']
    previous_page = answer.json()['previous']
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


def add_favorite_item_online_sellers(update, data):
    query = update.callback_query
    logger.debug(f'{update.effective_chat.id} выбирает онлайн торговцев')
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


def add_favorite_item_send_data(update, data):
    query = update.callback_query
    new_follow = {
        'lot': int(data['item_id']),
        'user': update.effective_chat.id,
        'server': int(data['server_id']),
    }
    answer = post_api_answer('following/', data=new_follow)
    response = answer.json()
    if answer.status_code != HTTPStatus.CREATED:
        text = ('Произошла ошибка при добавлении '
                f'избранного предмета в БД: {response}')
        message = 'Произошла ошибка при добавлении избранного предмета!'
        logger.error(text)
    else:
        text = f'Добавлен новый избранный предмет {new_follow} в БД'
        message = 'Избранный предмет успешно добавлен!'
        logger.debug(text)
    query.edit_message_text(text=message, parse_mode='HTML')


def change_favorite_item_monitoring(update, data):
    query = update.callback_query
    link = f'{URL}following/{data["item_id"]}/'
    is_monitoring = True
    if data["is_online"] == 'True':
        is_monitoring = False
    data = {
        'monitoring_online_sellers': is_monitoring
    }
    requests.patch(link, data=json.dumps(data), headers=HEADERS)
    message = 'Действие прошло успешно!'
    logger.debug('Пользователь изменил избранные предмет')
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
    actions[data['action']](update, data)
    logger.debug(f'{update.effective_chat.id} нажал на кнопку')


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
        MessageHandler(Filters.text('О проекте'), information)
    )

    updater.dispatcher.add_handler(
        CallbackQueryHandler(inline_buttons)
    )
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    asyncio.run(main())
