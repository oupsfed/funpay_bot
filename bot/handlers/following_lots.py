from http import HTTPStatus
from typing import Optional

from aiogram import Router, types
from aiogram.filters import Command, Text
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from magic_filter import F
from utils import (check_permissions, delete_api_answer, get_api_answer,
                   post_api_answer)

from messages import MESSAGES

from middlewares.is_staff import IsStaffMessageMiddleware

router = Router()
router.message.middleware(IsStaffMessageMiddleware())


class FollowingLotCallbackFactory(CallbackData, prefix='following_lots'):
    action: str
    following_lot_id: Optional[int]
    lot_id: Optional[int]
    server_id: Optional[int]
    user_id: Optional[int]
    monitoring_online_sellers: Optional[bool]
    page: Optional[int]


@router.message(Text('Избранные Товары'))
async def following_lots(message: types.Message):
    answer = get_api_answer('following/',
                            params={
                                'user__telegram_chat_id': message.chat.id
                            }
                            )
    lots = answer.json()
    lots = lots['results']
    builder = InlineKeyboardBuilder()
    for lot in lots:
        builder.button(
            text=lot["server"]["name"],
            callback_data=FollowingLotCallbackFactory(
                action='show',
                following_lot_id=lot['id'])
        )

    builder.button(
        text="Добавить",
        callback_data=FollowingLotCallbackFactory(
            action='add'
        ))
    builder.adjust(1)
    await message.answer(
        "Ваши избранные товары:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(FollowingLotCallbackFactory.filter(F.action == 'show'))
async def callbacks_show_following_lot(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    answer = get_api_answer(f'following/{callback_data.following_lot_id}')
    following_lot = answer.json()
    text = (f"Игра: <b>{following_lot['lot']['game']}</b>\n"
            f"Сервер: <b>{following_lot['server']['name']}</b>\n"
            f"Товар: <b>{following_lot['lot']['name']}</b>\n"
            f"Ссылка: <b>{following_lot['lot']['link']}</b>\n"
            f"<b>На данный момент цена: {following_lot['price']}</b> ₽")
    builder = InlineKeyboardBuilder()
    monitoring = 'Нет'
    if following_lot['monitoring_online_sellers']:
        monitoring = 'Да'
    builder.button(
        text=f'Следить за онлайн продавцами: {monitoring}',
        callback_data=FollowingLotCallbackFactory(
            action='change-monitoring',
            following_lot_id=following_lot['id']
        )
    )
    builder.button(
        text='Удалить',
        callback_data=FollowingLotCallbackFactory(
            action='delete',
            following_lot_id=following_lot['id']
        )
    )
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FollowingLotCallbackFactory.filter(F.action == 'change-monitoring'))
async def callbacks_change_monitoring(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    post_api_answer(f'following/'
                    f'{callback_data.following_lot_id}/'
                    f'change_monitoring/', data={})
    answer = get_api_answer(f'following/{callback_data.following_lot_id}')
    following_lot = answer.json()
    text = (f"Игра: <b>{following_lot['lot']['game']}</b>\n"
            f"Сервер: <b>{following_lot['server']['name']}</b>\n"
            f"Товар: <b>{following_lot['lot']['name']}</b>\n"
            f"Ссылка: <b>{following_lot['lot']['link']}</b>\n"
            f"<b>На данный момент цена: {following_lot['price']}</b> ₽")
    builder = InlineKeyboardBuilder()
    monitoring = 'Нет'
    if following_lot['monitoring_online_sellers']:
        monitoring = 'Да'
    builder.button(
        text=f'Следить за онлайн продавцами: {monitoring}',
        callback_data=FollowingLotCallbackFactory(
            action='change-monitoring',
            following_lot_id=following_lot['id']
        )
    )
    builder.button(
        text='Удалить',
        callback_data=FollowingLotCallbackFactory(
            action='delete'
        )
    )
    builder.adjust(1)
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FollowingLotCallbackFactory.filter(F.action == 'delete'))
async def callbacks_delete_following_lot(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    params = {
        'user__telegram_chat_id': callback.message.chat.id
    }
    delete_api_answer(f'following/{callback_data.following_lot_id}')
    answer = get_api_answer('following/',
                            params=params
                            )
    lots = answer.json()
    lots = lots['results']
    builder = InlineKeyboardBuilder()
    for lot in lots:
        builder.button(
            text=lot["server"]["name"],
            callback_data=FollowingLotCallbackFactory(
                action='show',
                following_lot_id=lot['id'])
        )

    builder.button(
        text="Добавить",
        callback_data=FollowingLotCallbackFactory(
            action='add'
        ))
    builder.adjust(1)
    await callback.message.edit_text(
        "Ваши избранные товары:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(
    FollowingLotCallbackFactory.filter(F.action == 'add'))
async def callbacks_add_following_lot(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    params = {
        'allow_monitoring': True
    }
    answer = get_api_answer('lots', params=params)
    lots = answer.json()['results']
    builder = InlineKeyboardBuilder()
    for lot in lots:
        builder.button(
            text=f'{lot["game"]} {lot["name"]}',
            callback_data=FollowingLotCallbackFactory(
                action='add-server',
                lot_id=lot['id'],
                page=1
            )
        )
    builder.adjust(1)
    text = 'Выберите Игру:'
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FollowingLotCallbackFactory.filter(F.action == 'add-server'))
async def callbacks_add_following_lot_step_2(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    params = {
        'game__lot__id': callback_data.lot_id,
        'page': callback_data.page
    }
    answer = get_api_answer('servers/',
                            params=params)
    servers = answer.json()['results']
    builder = InlineKeyboardBuilder()
    for server in servers:
        builder.button(
            text=server["name"],
            callback_data=FollowingLotCallbackFactory(
                action='select-monitoring',
                server_id=server['id'],
                lot_id=callback_data.lot_id
            )
        )
    if answer.json()['previous']:
        builder.button(
            text='Предыдущие',
            callback_data=FollowingLotCallbackFactory(
                action='add-server',
                lot_id=callback_data.lot_id,
                page=callback_data.page - 1
            )
        )
    if answer.json()['next']:
        builder.button(
            text='Следующие',
            callback_data=FollowingLotCallbackFactory(
                action='add-server',
                lot_id=callback_data.lot_id,
                page=callback_data.page + 1
            )
        )
    builder.adjust(1)
    text = 'Выберите сервер:'
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FollowingLotCallbackFactory.filter(F.action == 'select-monitoring'))
async def callbacks_add_following_lot_step_3(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Да',
        callback_data=FollowingLotCallbackFactory(
            action='add-lot-finish',
            lot_id=callback_data.lot_id,
            user_id=callback.message.chat.id,
            server_id=callback_data.server_id,
            monitoring_online_sellers=True
        )
    )
    builder.button(
        text='Нет',
        callback_data=FollowingLotCallbackFactory(
            action='add-lot-finish',
            lot_id=callback_data.lot_id,
            user_id=callback.message.chat.id,
            server_id=callback_data.server_id,
        )
    )
    builder.button(
        text='Назад',
        callback_data=FollowingLotCallbackFactory(
            action='add-server',
            lot_id=callback_data.lot_id,
            page=1
        )
    )
    builder.adjust(2)
    text = 'Следить только за онлайн продавцами?'
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FollowingLotCallbackFactory.filter(F.action == 'add-lot-finish'))
async def callbacks_add_following_lot_step_4(
        callback: types.CallbackQuery,
        callback_data: FollowingLotCallbackFactory
):
    following_lot = {
        'lot': callback_data.lot_id,
        'user': callback.message.chat.id,
        'server': callback_data.server_id,
        'monitoring_online_sellers': callback_data.monitoring_online_sellers
    }
    post_api_answer('following/', data=following_lot)
    await callback.message.edit_text('Избранный товар успешно добавлен')
