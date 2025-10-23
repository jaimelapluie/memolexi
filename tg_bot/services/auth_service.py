from aiogram import F, BaseMiddleware, Router
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.keyboards.words_kb import check_data_kb
from tg_bot.services.api_users import get_profile_by_telegram_id, get_token, put_token_to_local_db, get_existing_token
from tg_bot.states.profile import AuthStates
from tg_bot.states.words import AddWordProces


auth_router = Router()


@auth_router.message(AuthStates.waiting_for_password, ~F.text.startswith('/'))
async def handle_login_and_save_token(message: Message, state: FSMContext):
    """
    Ожидает пароль, пробует сделать запрос к API и получить токен и сохраняет его в
    локальную БД или возвращает сообщение об ошибочном пароле
    """
    
    print('\n>Отрабатывает service -> handle_login_and_save_token..')
    
    telegram_id = message.from_user.id
    password = message.text
    
    # Попытка получения профиля по telegram_id
    is_exist, data = await get_profile_by_telegram_id(telegram_id=telegram_id)
    if is_exist:
        print('get_profile_by_telegram_id получил профиль:', data)
        username = data.get("username")
    else:
        await state.clear()
        return await message.answer("Пользователь не найден")
        
    # Попытка получения токена
    user_data = {"username": username, "password": password}
    is_success, auth_token = await get_token(user_data)

    if is_success:
        print(f"auth_token: {auth_token}")
        await message.answer(f"Пароль верный. Успешно получены токены")
        user_data.pop("password")
        user_data.update(telegram_id=telegram_id)
        
        # Попытка сохранение токена в локальную БД
        is_done = await put_token_to_local_db(auth_token, user_data)
        if is_done:
            await state.clear()
            await message.answer('Теперь можно вернуться к первоначальному действию')
            # TODO: не нужны ли тут breadcrumbs? Возврат к первоначальному хэндлеру, или он сам?
            ##################################
            # print("Врубаю AddWordProces.waiting_check_state")
            #
            # # Возврат к состоянию
            # await state.set_state(AddWordProces.waiting_check_state)
            # print("Врубил <<")
            # await message.answer(text=f"Отлично, теперь вернемся к подтверждению действия по добавлению слова:",
            #                      reply_markup=check_data_kb())
            #############################################
            
        else:
            await message.answer(text='В handle_login_and_save_token произошла ошибка. '
                                      'Токен не сохранен в локальную базу')
    else:
        await message.answer(f"Вероятно введен неверный пароль, повторите попытку")
    print("Завершение работы handle_login_and_save_token")
    