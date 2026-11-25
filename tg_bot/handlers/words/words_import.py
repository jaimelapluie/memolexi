from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.filters import Command
from aiogram.filters import StateFilter

from tg_bot.services.api_words import send_file_to_api, send_text_to_api
from tg_bot.states.words import ImportWords
from io import BytesIO


import_words_router = Router()


@import_words_router.message(Command('import_words'))
async def handle_start_import_words(message: Message, state: FSMContext):
    """
    Хэндлер, начинающий процесс загрузки слов.
    :param state:
    :param message:
    :return:
    """
    await state.clear()
    await state.set_state(ImportWords.waiting_words)
    await message.answer(f'Пожалуйста, отправьте файл .xlsx/.docx/.txt/.md или текст со словами')

 
@import_words_router.message(StateFilter(ImportWords.waiting_words))
async def handle_import_words(message: Message, state: FSMContext, token: str):
    """
    Ожидает загрузки слов из файла (.xlsx/.docx/.txt/.md) или просто из текста сообщения.
    :param message:
    :param state:
    :param token:
    :return:
    """
    print('$$$$ handle_import_words')
    
    if message.document:
        file_name = (message.document.file_name or "").lower()
        if not file_name.endswith((".txt", ".md", ".docx", ".xlsx")):
            await message.answer("Поддерживаются только файлы .txt/.md/.xlsx")
            return
        
        print(f'> Получен Файл {file_name}')
        await message.answer(f'Получен файл "{file_name}"')
        
        buffer = BytesIO()
        bot = message.bot
        document = message.document
        await bot.download(document, destination=buffer)  # или bot.download_file(file_path, destination=buffer)
        buffer.seek(0)
        
        if not file_name.endswith((".docx", ".xlsx")):
            text = buffer.getvalue().decode("utf-8")  # bytes -> decode или buffer.read().decode("utf-8")
            print(text)
            await message.answer(f'Содержимое файла отправляем на бекенд:\n\n{text}')
        file_data = {'file_name': file_name, 'buffer': buffer, 'mime_type': message.document.mime_type}
        is_ok, words = await send_file_to_api(file_data=file_data, token=token)
        print(type(words))
        await message.answer(f'{words}')
        
    elif message.text:
        print(f'> Получен просто Текст')
        await message.answer(f'Полученный текст отправляем на бекенд:\n\n{message.text}')
        is_ok, words = await send_text_to_api(text=message.text, token=token)
        print(type(words))
        await message.answer(f'{words}')
    else:
        await message.answer(f'Пожалуйста, отправьте файл .xlsx/.txt или текст со словами')
