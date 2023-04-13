import json

import requests
from bs4 import BeautifulSoup as bs

from lots.models import Item, Lot, Server


def update_games_and_lots():
    URL = 'https://funpay.com/'
    r = requests.get(URL)
    soup = bs(r.text, "html.parser")
    games = soup.find('div', class_='promo-games-all')

    games = games.find('div', class_='promo-game-list')

    games = games.find_all('div', class_='promo-game-item')
    games_data = []
    lots_data = []
    for game in games:
        name = game.find('div', class_='game-title')
        locs = game.find_all('ul')
        is_servers = bool(game.find('div', class_='btn-group'))
        if is_servers:
            servers = game.find_all('button')
            for server in servers:
                games_data.append({
                    'name': name.text,
                    'loc': server.text,
                    'loc_id': server['data-id']
                })
        else:
            games_data.append({
                'name': name.text,
                'loc': '',
                'loc_id': name['data-id']
            })
        for loc in locs:
            for item in loc:
                if item.find('a') is not -1:
                    lots_data.append({
                        'loc_id': loc['data-id'],
                        'name': item.string,
                        'link': item.find('a')['href']
                    })
    games_url = 'http://127.0.0.1:8000/api/games/update_games/'
    lots_url = 'http://127.0.0.1:8000/api/games/update_lots/'
    headers = {'Content-type': 'application/json',
               'Content-Encoding': 'utf-8'}
    requests.post(games_url, data=json.dumps(games_data), headers=headers)
    requests.post(lots_url, data=json.dumps(lots_data), headers=headers)
    message = f'Updated {len(games_data)} games and {len(lots_data)} lots.'
    return message


def update_items():
    lots = Lot.objects.filter(allow_monitoring=True)
    data = []
    for lot in lots:
        Item.objects.filter(lot=lot).delete()
        r = requests.get(lot.link)
        soup = bs(r.text, "html.parser")
        items = soup.find_all('a', class_='tc-item')
        for item in items:
            server = item.find('div', class_='tc-server')
            seller = item.find('div', class_='media-user-name')
            item_name = item.find('div', class_='tc-desc-text')
            amount = item.find('div', class_='tc-amount')
            price = item.find('div', class_='tc-price')
            online = bool(item.find('div', class_='online'))

            if item_name is None:
                item_name = 'Валюта'
            else:
                item_name = item_name.text

            if amount is None:
                amount = 1
            else:
                amount = amount.text
                amount = int(amount[:amount.find(' ')])

            if server:
                server = server.string
                Server.objects.get_or_create(
                    name=server,
                    game=lot.game
                )
                server = Server.objects.get(name=server)
            price = price.text.strip()
            price = float(price[:price.find(' ')])
            data.append(Item(
                server=server,
                seller=seller.string.strip(),
                name=item_name,
                amount=amount,
                price=price,
                link=item['href'],
                online=online,
                lot=lot
            ))
    Item.objects.bulk_create(data)
    return f'Updated {len(data)} items'
