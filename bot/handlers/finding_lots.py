from aiogram import Router, types
from aiogram.filters import Text

router = Router()


@router.message(Text('Поиск Товара'))
async def finding_lots(message: types.Message):
    await message.reply("Отличный выбор!")
