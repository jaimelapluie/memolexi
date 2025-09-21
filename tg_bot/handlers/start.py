import asyncio

import httpx
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import StateFilter
from aiogram.utils.chat_action import ChatActionSender

from tg_bot.config import bot_instance
from tg_bot.services.api_users import get_existing_token

start_router = Router()


@start_router.message(StateFilter(None), ~F.text.startswith("/"))
async def simple_echo(message: Message, state: FSMContext):
    """Тестовая функция. Перехватывает сообщения и отвечает тут же, но только если state=None """
    print(message.text)
    await message.answer(message.text)
    

@start_router.message(F.text == "/help")
async def start_handler(message: Message, state: FSMContext):
    """Временный хэндлер, просмотр слов"""
    
    if message.from_user.id not in (459483895, 240753763):
        await message.answer('Ошибка доступа')
        return
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get("http://127.0.0.1:8000/words/")
            response.raise_for_status()
            row_words = response.json()
            words = row_words['results']
            text = "start_handler - ошибка. Слов нет"
            if len(words):
                print(words)
                text = ''
                await message.answer('ХМмм') if len(words) else ""
                for dict_word in words:
                    for k, v in dict_word.items():
                        print(k, v)
                        text += f"{str(k)}: {str(v)} \n"
        
        except httpx.HTTPError as err:
            print(f"Ошибка при запросе:{err}")
            text = f"Ошибка при запросе:{err}"
        
        await message.answer(text)
    
    
@start_router.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    """Тестовый хэндлер, приветствие нового пользователя"""

    await state.clear()
    if message.from_user.id not in (459483895, 240753763):
        await message.answer('Ошибка доступа')
    else:
        print('Зашел в start_handler')
        print(message.chat.id)
        print(message.chat.username)
        async with ChatActionSender.typing(bot=bot_instance, chat_id=message.chat.id):
            await asyncio.sleep(0.5)
            await message.answer('Тестовый запуск. start_handler отработал')
        # caption = (f'password: ||"password"||')

        # await message.answer(text=caption, parse_mode='MarkdownV2')
        await message.answer(f"Привет\\! Запускаю анкетирование Memolexi ||Скрытый господин||",
                             parse_mode='MarkdownV2')  # , reply_markup=menu_kb()

        # в качестве эксперимента обращаюсь к API
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get("http://127.0.0.1:8000/users/")
                response.raise_for_status()
                users = response.json()
                print(users)
                text = ''
                for user in users:
                    for k, v in user.items():
                        print(k, v)
                        text += f"{str(k)}: {str(v)} \n"

            except httpx.HTTPError as err:
                print(f"Ошибка при запросе:{err}")
                text = f"Ошибка при запросе:{err}"

            await message.answer(text)
        # await message.answer('Удаляю клаву', reply_markup=ReplyKeyboardRemove())
        print('конец теста')
