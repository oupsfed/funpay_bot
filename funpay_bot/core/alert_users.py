import os

from dotenv import load_dotenv
from telegram import Bot

from lots.models import FollowingLot, Item

load_dotenv()

token = os.getenv('TOKEN')

bot = Bot(token=token)


def alert():
    items = Item.objects.all()
    following_lots = FollowingLot.objects.all()
    count = 0
    for following_lot in following_lots:
        price = items.filter(
            server=following_lot.server).values_list('price', flat=True)
        if following_lot.monitoring_online_sellers:
            price = items.filter(
                server=following_lot.server,
                online=True).values_list('price', flat=True)
        if not following_lot.price or not (following_lot.price == min(price)):
            following_lot.price = min(price)
            following_lot.save()
            item = items.filter(
                server=following_lot.server,
                price=min(price)).first()
            message = f'''
Цена <b>{following_lot.lot.name}</b> изменилась на <b>{min(price)} ₽</b>
Игра: <b>{following_lot.lot.game}</b>
Сервер: <b>{following_lot.server}</b>
Количество: <b>{item.amount}</b>
Ссылка: <b>{item.link}</b>
'''
            global bot
            bot.send_message(
                following_lot.user.telegram_chat_id,
                message,
                parse_mode="html"
            )
            count += 1
    return f'Alerted {count} users.'
