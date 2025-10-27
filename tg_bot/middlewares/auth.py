from aiogram import F, BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from tg_bot.services.api_users import get_existing_token
from tg_bot.states.profile import AuthStates


reserved_commands_list = ('/start', '/profile', '/help')


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
        print(f"\n\nAuthMiddleware в работе {"*" * 50}")
        telegram_id = event.from_user.id
        state = data['state']
        current_state = await state.get_state()

        # Пропускаю зарезервированные команды, callback и состояние ожидания пароля
        if (
            isinstance(event, CallbackQuery)
            or (isinstance(event, Message) and event.text in reserved_commands_list)
            or current_state == "AuthStates:waiting_for_password"
        ):
            return await handler(event, data)  # Вызов исходного хэндлера без пароля

        # запрос токена из локальной БД
        is_token_exist, access_token = await get_existing_token(telegram_id)
        
        if is_token_exist:
            data['token'] = access_token
            return await handler(event, data)  # Вызов исходного хэндлера

        # токена нет и состояние не AuthStates:waiting_for_password
        if current_state != "AuthStates:waiting_for_password":
            await state.set_state(AuthStates.waiting_for_password)
            await event.answer('Пожалуйста, введите пароль!')
            await state.update_data(original_command=event.text)

"""
fix(bot): Add callback handle, return to original handler from middleware

- Implement callback at AuthMiddleware: push bots' button handle without error
- Ensure logic to seamless return to original handler after correct password input
"""