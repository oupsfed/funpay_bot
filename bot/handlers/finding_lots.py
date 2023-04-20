from typing import Optional

from aiogram import Router, types, F
from aiogram.filters import Text
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from middlewares.is_staff import IsStaffMessageMiddleware
from utils import get_api_answer, post_api_answer


router = Router()
router.message.middleware(IsStaffMessageMiddleware())


class AddFindingLot(StatesGroup):
    choosing_name = State()


class FindingLotCallbackFactory(CallbackData, prefix='finding_lots'):
    action: str
    finding_lot_id: Optional[int]
    lot_id: Optional[int]
    server_id: Optional[int]
    user_id: Optional[int]
    monitoring_online_sellers: Optional[bool]
    page: Optional[int]


@router.message(Text('Поиск Товара'))
async def finding_lots(message: types.Message):
    answer = get_api_answer('finding/',
                            params={
                                'user__telegram_chat_id': message.chat.id
                            }
                            )
    lots = answer.json()
    lots = lots['results']
    builder = InlineKeyboardBuilder()
    for lot in lots:
        builder.button(
            text=f'{lot["name"]} - {lot["server"]["name"]}',
            callback_data=FindingLotCallbackFactory(
                action='show',
                finding_lot_id=lot['id'])
        )

    builder.button(
        text="Добавить",
        callback_data=FindingLotCallbackFactory(
            action='add'
        ))
    builder.adjust(1)
    await message.answer(
        "Ваши товары в поиске:",
        reply_markup=builder.as_markup()
    )


@router.callback_query(
    FindingLotCallbackFactory.filter(F.action == 'add'))
async def callbacks_add_finding_lot(
        callback: types.CallbackQuery,
        callback_data: FindingLotCallbackFactory
):
    params = {
        'allow_finding': True
    }
    answer = get_api_answer('lots', params=params)
    lots = answer.json()['results']
    builder = InlineKeyboardBuilder()
    for lot in lots:
        builder.button(
            text=f'{lot["game"]} {lot["name"]}',
            callback_data=FindingLotCallbackFactory(
                action='add-server',
                lot_id=lot['id'],
                page=1
            )
        )
    builder.adjust(1)
    text = 'Выберите Игру:'
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FindingLotCallbackFactory.filter(F.action == 'add-server'))
async def callbacks_add_finding_lot_step_2(
        callback: types.CallbackQuery,
        callback_data: FindingLotCallbackFactory,
        state: FSMContext
):
    params = {
        'game__lot__id': callback_data.lot_id,
        'page': callback_data.page
    }
    answer = get_api_answer('servers/',
                            params=params)
    servers = answer.json()['results']
    builder = InlineKeyboardBuilder()
    await state.update_data(lot_id=callback_data.lot_id)
    for server in servers:
        builder.button(
            text=server["name"],
            callback_data=FindingLotCallbackFactory(
                action='add-name',
                server_id=server['id'],
                lot_id=callback_data.lot_id
            )
        )
    if answer.json()['previous']:
        builder.button(
            text='Предыдущие',
            callback_data=FindingLotCallbackFactory(
                action='add-server',
                lot_id=callback_data.lot_id,
                page=callback_data.page - 1
            )
        )
    if answer.json()['next']:
        builder.button(
            text='Следующие',
            callback_data=FindingLotCallbackFactory(
                action='add-server',
                lot_id=callback_data.lot_id,
                page=callback_data.page + 1
            )
        )
    builder.adjust(1)
    text = 'Выберите сервер:'
    await callback.message.edit_text(text, reply_markup=builder.as_markup())


@router.callback_query(
    FindingLotCallbackFactory.filter(F.action == 'add-name'))
async def callbacks_add_finding_lot_step_2(
        callback: types.CallbackQuery,
        callback_data: FindingLotCallbackFactory,
        state: FSMContext
):
    await state.update_data(server_id=callback_data.server_id)
    await callback.message.edit_text(
        text='Введите название предмета'
    )
    await state.set_state(AddFindingLot.choosing_name)


@router.message(AddFindingLot.choosing_name, F.text)
async def callbacks_add_finding_lot_step_3(message: Message, state: FSMContext):
    await state.update_data(name=message.text,
                            user=message.chat.id)
    data = await state.get_data()
    finding_lot = {
        'lot': data['lot_id'],
        'user': data['user'],
        'server': data['server_id'],
        'name': data['name']
    }
    post_api_answer('finding/', data=finding_lot)
    await state.clear()
    await message.answer('Товар для поиска успешно добавлен')



