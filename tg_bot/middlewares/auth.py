from aiogram import F, BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from tg_bot.services.api_users import get_existing_token
from tg_bot.states.profile import AuthStates


class AuthMiddleware(BaseMiddleware):
    """
    Перехватывает выполнение хэндлеров, получает токен из локальной базы
    или перенаправляет к вводу пароля
    """
    
    async def __call__(self,
                       handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
                       event: Message | CallbackQuery,
                       data: Dict[str, Any]
                       ) -> Any:
        print("\n\nAuthMiddleware в работе")
        telegram_id = event.from_user.id
        state = data['state']
        current_state = await state.get_state()
        
        if current_state == "AuthStates:waiting_for_password":
            return await handler(event, data)  # Вызов auth хэндлера, чтобы не попасть в loop
        
        # запрос токена из локальной БД
        is_token_exist, access_token = await get_existing_token(telegram_id)
        
        if is_token_exist:
            data['token'] = access_token
            return await handler(event, data)  # Вызов исходного хэндлера
        
        else:
            await state.set_state(AuthStates.waiting_for_password)
            await event.answer('Пожалуйста, введите пароль')
            return
