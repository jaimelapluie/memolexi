from aiogram import F, Router

from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from tg_bot.config import bot_instance
from tg_bot.handlers.words.listing import handle_view_words
from tg_bot.handlers.words.new_adding import handle_add_word_command
from tg_bot.keyboards.words_kb import check_data_kb

from tg_bot.services.api_users import get_profile_by_telegram_id, get_token, put_token_to_local_db, get_existing_token
from tg_bot.states.profile import AuthStates

auth_router = Router()

command_map = {
                '/view_words': {
                    'handler': handle_view_words,
                    'prompt': 'Возобновляю показ слов'},
                '/add_word': {
                    'handler': handle_add_word_command,
                    'prompt': 'Возобновляю процесс добавления слова'},
                '/srs': {
                    'handler': 'RESERVED',  # TODO: добавить когда напишу
                    'prompt': 'srs_reserved'},
                
                }


@auth_router.message(AuthStates.waiting_for_password, F.text.startswith('/'))
async def cancel_auth_on_command(message: Message, state: FSMContext):
    """
    Хэндлер сбрасывает процесс ожидания пароля в случае ввода другой команды
    """
    print('\ncancel_auth_on_command Ввод пароля прерван другой командой')
    await state.clear()
    await message.answer(f'Ввод пароля прерван командой {message.text}')


@auth_router.message(AuthStates.waiting_for_password, ~F.text.startswith('/'))  # ~F.text.startswith('/')
async def handle_login_and_save_token(message: Message, state: FSMContext):
    """
    Ожидает пароль, пробует сделать запрос к API и получить токен и сохраняет его в
    локальную БД или возвращает сообщение об ошибочном пароле
    """
    
    print('\n>Отрабатывает service -> handle_login_and_save_token..')
    data = await state.get_data()
    original_handler = data.get('original_handler')
    print(f"original_handler = {original_handler}")
    
    telegram_id = message.from_user.id
    password = message.text
    print(f"password = {password}")
    
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
        await message.answer(f"Пароль верный")
        user_data.pop("password")
        user_data.update(telegram_id=telegram_id)
        
        # Попытка сохранение токена в локальную БД
        is_done = await put_token_to_local_db(auth_token, user_data)
        if is_done:
            # TODO: Возврат к первоначальному хэндлеру через feed_raw_update?
            # Извлекаем сохранённую команду
            data = await state.get_data()
            original_command = data.get('original_command')
            
            await state.clear()  # Очищаем состояние после авторизации
            
            if original_command and not original_command.startswith('/'):
                await message.answer('Теперь можете повторить команду')
                return
                
            if original_command:
                command_config = command_map.get(original_command)
                original_handler = command_config.get('handler')
                prompt = command_config.get('prompt')
                await message.answer(prompt)
                await original_handler(message, state)
            
        else:
            await message.answer(text='В handle_login_and_save_token произошла ошибка. '
                                      'Токен не сохранен в локальную базу')
    else:
        await message.answer(f"Вероятно введен неверный пароль, повторите попытку")
    print("Завершение работы handle_login_and_save_token")
    