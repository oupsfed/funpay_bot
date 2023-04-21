import logging
import os

from dotenv import load_dotenv
from telegram import Bot

from lots.models import FindingLot, FollowingLot, Item

load_dotenv()

token = os.getenv('TOKEN')

bot = Bot(token=token)


def check_price(items, lots):
    count = 0
    for lot in lots:
        price = items.filter(
            server=lot.server,
            name=None).values_list('price', flat=True)
        if lot.monitoring_online_sellers:
            price = items.filter(
                server=lot.server,
                name=None,
                online=True
            ).values_list('price', flat=True)
        if price:
            price = min(price)
            if lot.price != price:
                lot.price = price
                lot.save()
                item = items.filter(
                    server=lot.server,
                    price=price).first()
                message = (f'Цена <b>{lot.lot.name}</b> '
                           f'изменилась на <b>{price} ₽</b>\n'
                           f'Игра: <b>{lot.lot.game}</b>\n'
                           f'Сервер: <b>{lot.server}</b>\n'
                           f'Количество: <b>{item.amount} кк</b>\n'
                           f'Ссылка: <b>{item.link}</b>')
                bot.send_message(
                    lot.user.telegram_chat_id,
                    message,
                    parse_mode="html"
                )
                count += 1
                logging.info(f'Alerted '
                             f'{lot.user.telegram_chat_id} '
                             f'for {lot.lot.name}')
    return count


def check_items(items, lots):
    count = 0
    for lot in lots:
        price = items.filter(
            server=lot.server,
            name__icontains=lot.name).values_list('price', flat=True)
        if lot.monitoring_online_sellers:
            price = items.filter(
                server=lot.server,
                name__icontains=lot.name,
                online=True
            ).values_list('price', flat=True)
        if price:
            price = min(price)
            if lot.price != price:
                lot.price = price
                lot.save()
                item = items.filter(
                    server=lot.server,
                    name__icontains=lot.name,
                    price=price).first()
                message = (f'Появился предмет: <b>{item.name}</b>\n'
                           f'Цена: <b>{item.price} ₽</b>\n'
                           f'Сервер: <b>{lot.server}</b>\n'
                           f'Ссылка: <b>{item.link}</b>')
                bot.send_message(
                    lot.user.telegram_chat_id,
                    message,
                    parse_mode="html"
                )
                count += 1
                logging.info(f'Alerted '
                             f'{lot.user.telegram_chat_id} '
                             f'for {lot.lot.name}')
    return count


def alert():
    items = Item.objects.all()
    following_lots = FollowingLot.objects.all()
    finding_lots = FindingLot.objects.all()
    alerted = check_price(items, following_lots)
    alerted += check_items(items, finding_lots)
    return f'Alerted {alerted} users'
