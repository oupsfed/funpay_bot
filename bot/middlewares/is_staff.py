from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from utils import get_api_answer


def is_staff(user_id) -> bool:
    answer = get_api_answer(f'users/{user_id}')
    return answer.json()['is_staff']


class IsStaffMessageMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if is_staff(event.chat.id):
            return await handler(event, data)
        await event.answer(
            "Доступ только для администратора",
            show_alert=True
        )
        return


class IsStaffCallbackMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        # Если сегодня не суббота и не воскресенье,
        # то продолжаем обработку.
        if is_staff(event.chat.id):
            return await handler(event, data)
        # В противном случае отвечаем на колбэк самостоятельно
        # и прекращаем дальнейшую обработку
        await event.answer(
            "Доступ только для администратора",
            show_alert=True
        )
        return
