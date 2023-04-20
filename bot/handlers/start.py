from aiogram import Router, types
from aiogram.filters import Command, ChatMemberUpdatedFilter, KICKED
from aiogram.types import ChatMemberUpdated
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from utils import (check_permissions, delete_api_answer, get_api_answer,
                   post_api_answer)

from messages import MESSAGES


router = Router()


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    user = message.chat
    answer = get_api_answer('users/',
                            params={
                                'telegram_chat_id': user.id
                            })
    if answer.json()['count'] == 0:
        data = {
            'first_name': user.first_name,
            'last_name': user.last_name,
            'telegram_chat_id': user.id,
            'username': user.username
        }
        post_api_answer('users/', data)
    builder = ReplyKeyboardBuilder()
    builder.row(
        types.KeyboardButton(text="Избранные Товары"),
        types.KeyboardButton(text="Поиск Товара"),
    )
    builder.row(
        types.KeyboardButton(text="Информация"),
    )

    await message.answer(MESSAGES['start'],
                         parse_mode='HTML',
                         reply_markup=builder.as_markup(resize_keyboard=True))


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    delete_api_answer(f'users/{event.from_user.id}')
