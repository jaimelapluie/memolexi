from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tg_bot.keyboards.profile_kb import get_edit_delete_profile_kb
from tg_bot.services.api_users import get_token, get_profile_by_telegram_id, api_delete_profile, get_existing_token
from tg_bot.states.profile import AuthStates, DeleteProfile

delete_profile_router = Router()


# TODO: рефакторинг кода сделать: возможно стоит сразу проверять наличие токена, без проверки наличия юзера
@delete_profile_router.message(AuthStates.login_password)
async def login_and_save_token(message: Message, state: FSMContext):
    """Отрабатывет для получения токена"""
    
    await message.answer("Реализуется выполнение login_and_save_token")
    
    password = message.text
    is_exist, data = await get_profile_by_telegram_id(telegram_id=message.from_user.id)
    if is_exist:
        print(data)
        print(type(data))
        username = data.get("username")
    else:
        return await message.answer("Пользователь не найден")
    
    user_data = {"username": username, "password": password}
    is_success, auth_token = await get_token(user_data)
    
    if is_success:
        await message.answer(f"Успешно получены токены")
        await state.update_data(token=auth_token)
        await message.answer(f"Пароль верный. Подтвердите действие:", reply_markup=get_edit_delete_profile_kb())
    else:
        await message.answer(f"{auth_token}. Введите верный пароль")
    
    await message.answer("Завершение работы login_and_save_token")
    

@delete_profile_router.callback_query(F.data == "delete_profile")
async def delete_profile(call: CallbackQuery, state: FSMContext):
    """Профиль -> Отработка кнопки Удалить"""
    
    print('\nОтрабатывает delete_profile')
    await state.clear()
    telegram_id = call.from_user.id
    
    # запрос токена из локальной БД
    is_token_exist, access_token = await get_existing_token(telegram_id)
    print("получил от get_existing_token(telegram_id) token=", access_token)
    
    # TODO: добавить подтверджение удаления
    if is_token_exist:
        is_deleted, response = await api_delete_profile(access_token)
        if is_deleted:
            await call.message.answer(f"Профиль успешно удалён.", reply_markup=None)
        else:
            await call.message.answer(f"Что-то пошло не так. {response}", reply_markup=None)
    
    else:
        # токена нету, запрашиваю пароль
        await call.message.answer('Пожалуйста, введите пароль для подтверждения удаления профиля')
        await state.set_state(AuthStates.login_password)
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
