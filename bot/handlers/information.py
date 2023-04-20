from aiogram import Router, types
from aiogram.filters import Text
from aiogram.utils.keyboard import InlineKeyboardBuilder

from utils import get_api_answer
from messages import MESSAGES

router = Router()


@router.message(Text('Информация'))
async def finding_lots(message: types.Message):
    users = get_api_answer('users',
                           params={
                               'is_staff': True,
                           })
    users_count = users.json()['count']
    following_lots = get_api_answer('lots',
                                    params={
                                        'allow_monitoring': True
                                    })
    following_lots = following_lots.json()['results']
    finding_lots = get_api_answer('lots',
                                  params={
                                      'allow_finding': True
                                  })
    finding_lots = finding_lots.json()['results']
    text = MESSAGES['information']
    text += 'Доступные товары для мониторинга цен:\n'
    for following_lot in following_lots:
        text += (f"- <b>{following_lot['game']} "
                 f"- {following_lot['name']}</b>\n")
    text += 'Доступные товары для поиска:\n'
    for finding_lot in finding_lots:
        text += (f"- <b>{finding_lot['game']} "
                 f"- {finding_lot['name']}</b>\n")
    text += f"Пользователей в ЗБТ: <b>{users_count}</b>\n"
    text += 'Доступные товары будут дополняться по мере загрузки бота.'
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Заявка на ЗБТ',
        url='https://forms.gle/ZmYzyokdYWUgEzCN9'
    )
    await message.answer_photo('https://ltdfoto.ru/images/2023/04/14/tg.png')
    await message.reply(text, reply_markup=builder.as_markup())
