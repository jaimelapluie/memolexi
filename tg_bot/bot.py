import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
import asyncio
import os

from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv

# из статьи на хабре
import asyncio
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from keyboards import language_kb, get_login_tg_kb, check_data_kb
from utils import extract_number
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()  # Загружает токен из .env файла

bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties())
# dp = Dispatcher()
dp = Dispatcher(storage=MemoryStorage())


# начало примера


class Form(StatesGroup):
    name = State()
    language = State()
    username = State()
    email = State()
    password = State()
    check_state = State()


questionnaire_router = Router()
kek = Router()


@questionnaire_router.message(Command('start_questionnaire'))
async def start_questionnaire_process(message: Message, state: FSMContext):
    print('A')
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.answer('Привет, для удобства и возможности доступа к сервису вне пределах telegram, '
                             'заполни анкету из 5 пунктов. Для начала напиши своё имя - как к тебе обращаться: ')
    await state.set_state(Form.name)


@questionnaire_router.message(F.text, Form.name)
async def questionnaire_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        await message.answer(f'Приятно познакомиться, {message.text}! А какой основной язык ты сейчас учишь?',
                             reply_markup=language_kb())
    await state.set_state(Form.language)


@questionnaire_router.message((F.text.lower().contains('английский') | F.text.lower().contains('eng') |
                               F.text.lower().contains('english') |
                               F.text.lower().contains('испанский') | F.text.lower().contains('span') |
                               F.text.lower().contains('spanish')), Form.language)
async def questionnaire_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer('Инфа принята!', reply_markup=ReplyKeyboardRemove())
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(1)
        data = await state.get_data()
        name = data.get('name')
        text = (f'Круто, {name}! А теперь придумай себе username - ведь в будущем, когда этот бот '
                f'выберется за пределы телеграм в Интернет... хо-хо, сможешь подключиться к своей'
                f'Базе Знаний через другой ресурс, например через сайт.')

        if message.from_user.username:
            await message.answer(text)
            await asyncio.sleep(1)
            await message.answer('Можешь использовать свой username из телеграм. Ща я его достану.. ',
                                 reply_markup=get_login_tg_kb())
        else:
            text += ' : '
            await message.answer(text)
    await state.set_state(Form.username)


# вариант когда мы берем логин из профиля телеграм
@questionnaire_router.callback_query(F.data, Form.username)
async def questionnaire_username(call: CallbackQuery, state: FSMContext):
    await call.answer('Окей, использую твой username из телеграм')
    await call.message.edit_reply_markup(reply_markup=None)
    await state.update_data(username=call.from_user.username)
    await call.message.answer('Осталась пара пустяков: укажи свой email:')
    await state.set_state(Form.email)


# вариант когда мы берем логин введенный
@questionnaire_router.message(F.text, Form.username)
async def questionnaire_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text)
    await message.answer('Осталась пара пустяков: укажи свой email:')
    await state.set_state(Form.email)


@questionnaire_router.message(F.text, Form.email)
async def questionnaire_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer('Ну и последнее: укажи свой password:')
    await state.set_state(Form.password)


@questionnaire_router.message(F.text, Form.password)
async def questionnaire_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    
    caption = (f'Проверь, всё ли корректно? \n\n'
               f'Имя: {data.get("name")} \n'
               f'Основной язык: {data.get("language")} \n'
               f'username: {data.get("username")} \n'
               f'email: {data.get("email")} \n'
               f'password: {data.get("password")}')
    
    await message.answer(text=caption, reply_markup=check_data_kb())
    await state.set_state(Form.check_state)


# сохраняю данные
@questionnaire_router.callback_query(F.data == 'correct', Form.check_state)
async def questionnaire_check_state(call: CallbackQuery, state: FSMContext):
    await call.answer('Данные сохранены, спасибо')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Благодарю за регистрацию. Ваши данные успешно сохранены!')
    await state.clear()


# запускаем анкету сначала
@questionnaire_router.callback_query(F.data == 'incorrect', Form.check_state)
async def questionnaire_check_state(call: CallbackQuery, state: FSMContext):
    await call.answer('Видимо что-то напутали, давай по-новой!')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Последовательность вопросв анкеты ты помнишь, начнем с имени:')
    await state.set_state(Form.name)


@dp.message(F.text == "/start")
async def start_handler(message: Message):
    print('Зашел в start_handler')
    print(message.chat.id)
    print(message.chat.username)
    # await message.answer("Выберите действие:", reply_markup=inline_keyboard)
    # await message.answer("Выберите действие:", reply_markup=keyboard)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(3)
        await message.answer('Супер! start_handler отработал')
    # caption = (f'password: ||"password"||')
    #
    # await message.answer(text=caption, parse_mode='MarkdownV2')
    await message.answer(f"Привет\\! Я твой бот Memolexi ||Скрытый господин||",
                         parse_mode='MarkdownV2')


# @dp.message()
# async def get_words(message: Message):
#     async with httpx.AsyncClient() as client:
#         response = await client.get("http://127.0.0.1:8000/words/")
#         response = await client.get("http://127.0.0.1:8000/words/?limit=2&offset=6")
#         res = ''
#         for elem in response.json()["results"]:
#             print('!!!!elem')
#             print(elem)
#             res += elem.get('word') + ' '
#
#         await message.answer(res)
# return response.json()["results"]


f = [{'id': 52, 'word': 'mention', 'translation': 'упомянуть\xa0_**|**\xa0упоминать, отметить_',
      'example': 'Other notable\xa0_mention_s are Sushi Zanmai,', 'source':
          '[youtube.com](https://www.youtube.com/watch?v=2_Ghl3I9PpM)',
      'reverso_url': 'https://context.reverso.net/translation/english-russian/mention',
      'picture': None, 'time_create': '2025-04-14T10:15:38.037927Z', 'author': 'res', 'word_lists': ['master_list']},
     {'id': 51, 'word': 'notable', 'translation': 'заметный\xa0_**|**\xa0известный, примечательный_',
      'example': None, 'source': None, 'reverso_url': 'https://context.reverso.net/translation/english-russian/notable',
      'picture': None, 'time_create': '2025-04-14T10:15:38.015978Z', 'author': 'res', 'part_of_speech': 'noun',
      'word_lists': ['master_list']}]

dp.include_router(questionnaire_router)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
