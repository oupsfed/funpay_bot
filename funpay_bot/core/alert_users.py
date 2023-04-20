import os

from dotenv import load_dotenv
from lots.models import FollowingLot, Item, FindingLot
from telegram import Bot

load_dotenv()

token = os.getenv('TOKEN')

bot = Bot(token=token)


def alert():
    items = Item.objects.all()
    following_lots = FollowingLot.objects.all()
    finding_lots = FindingLot.objects.all()
    count = 0
    global bot
    for following_lot in following_lots:
        price = items.filter(
            server=following_lot.server,
            name='Валюта').values_list('price', flat=True)
        if following_lot.monitoring_online_sellers:
            price = items.filter(
                server=following_lot.server,
                name='Валюта',
                online=True).values_list('price', flat=True)
        if not following_lot.price or not (following_lot.price == min(price)):
            following_lot.price = min(price)
            following_lot.save()
            item = items.filter(
                server=following_lot.server,
                price=min(price)).first()
            message = (f'Цена <b>{following_lot.lot.name}</b> '
                       f'изменилась на <b>{min(price)} ₽</b>\n'
                       f'Игра: <b>{following_lot.lot.game}</b>\n'
                       f'Сервер: <b>{following_lot.server}</b>\n'
                       f'Количество: <b>{item.amount} кк</b>\n'
                       f'Ссылка: <b>{item.link}</b>')
            bot.send_message(
                following_lot.user.telegram_chat_id,
                message,
                parse_mode="html"
            )
            count += 1
    for finding_lot in finding_lots:
        price = items.filter(
            server=finding_lot.server,
            name__icontains=finding_lot.name,).values_list('price', flat=True)
        if finding_lot.monitoring_online_sellers:
            price = items.filter(
                server=finding_lot.server,
                name__icontains=finding_lot.name,
                online=True).values_list('price', flat=True)
        if not finding_lot.price or not (finding_lot.price == min(price)):
            finding_lot.price = min(price)
            finding_lot.save()
            item = items.filter(
                server=finding_lot.server,
                price=min(price)).first()
            message = (f'По вашему запросу - <b>{finding_lot.name}'
                       f'- {finding_lot.server}</b>\n'
                       f'Найден предмет - <b>{item.name}</b>\n'
                       f'Цена <b>{item.price}</b>\n'
                       f'Ссылка: <b>{item.link}</b>')
            bot.send_message(
                finding_lot.user.telegram_chat_id,
                message,
                parse_mode="html"
            )
            count += 1
    return f'Alerted {count} users.'
