import httpx
from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message
import asyncio
import os

from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv

import asyncio
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.utils.chat_action import ChatActionSender
from keyboards import language_kb, get_login_tg_kb, check_data_kb, menu_kb, set_default_commands, \
    edit_delete_profile_kb, edit_kb
from tg_bot.services import is_username_exists, get_profile_by_telegram_id, create_user, update_user_data
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


class EditProfile(StatesGroup):
    edit_mode = State()
    username = State()
    password = State()
    first_name = State()
    email = State()
    main_language = State()


edit_profile_router = Router()


# @questionnaire_router.message(F.text == 'Регистрация')
# async def questionnaire_check_state(message: Message, state: FSMContext):
#     print("зашел сюда")
#     await message.answer('Привет, для удобства и возможности доступа к сервису вне пределах telegram, '
#                          'заполни анкету из 5 пунктов. Для начала напиши своё имя - как к тебе обращаться: ',
#                          reply_markup=ReplyKeyboardRemove())
#     # await state.set_state(Form.name)


@questionnaire_router.message(Command('start_questionnaire'))
async def start_questionnaire_process(message: Message, state: FSMContext):
    print('A')
    await state.clear()
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(0.5)
        await message.answer('Привет, для удобства и возможности доступа к сервису вне пределах telegram, '
                             'заполни анкету из 5 пунктов. Для начала напиши своё имя - как к тебе обращаться: ')
    await state.set_state(Form.name)


@questionnaire_router.message(F.text, Form.name)
async def questionnaire_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(0.5)
        await message.answer(f'Приятно познакомиться, {message.text}! А какой основной язык ты сейчас учишь?',
                             reply_markup=language_kb())
    await state.set_state(Form.language)


@questionnaire_router.message((F.text.lower().contains('английский') | F.text.lower().contains('eng') |
                               F.text.lower().contains('english') |
                               F.text.lower().contains('испанский') | F.text.lower().contains('esp') |
                               F.text.lower().contains('espanol')), Form.language)
async def questionnaire_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer('Инфа принята!', reply_markup=ReplyKeyboardRemove())
    async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
        await asyncio.sleep(0.5)
        data = await state.get_data()
        name = data.get('name')
        text = (f'Круто, {name}! А теперь придумай себе username - ведь в будущем, когда этот бот '
                f'выберется за пределы телеграм в Интернет... хо-хо, сможешь подключиться к своей '
                f'Базе Знаний через другой ресурс, например через сайт')
        
        if message.from_user.username:
            await message.answer(text)
            await asyncio.sleep(0.5)
            await message.answer('Можешь использовать свой username из телеграм. Ща я его достану.. ',
                                 reply_markup=get_login_tg_kb())
        else:
            text += ' : '
            await message.answer(text)
    await state.set_state(Form.username)


# вариант когда мы берем логин из профиля телеграм
@questionnaire_router.callback_query(F.data, Form.username)
async def questionnaire_username(call: CallbackQuery, state: FSMContext):
    print('вариант когда мы берем логин из профиля телеграм')
    username = call.from_user.username
    is_exists, text = await is_username_exists(username)
    print(is_exists, text)
    if is_exists:
        await call.answer(text)
        return
    
    await call.message.answer(text)
    # если username свободен, иду по сценарию дальше
    await call.message.answer('Окей, использую твой username из телеграм')
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    
    await state.update_data(username=call.from_user.username)
    await call.message.answer('Осталась пара пустяков: укажи свой email:')
    await state.set_state(Form.email)


# вариант когда мы берем логин введенный
@questionnaire_router.message(F.text, Form.username)
async def questionnaire_username(message: Message, state: FSMContext):
    print('вариант когда мы берем логин введенный')
    username = message.text
    is_exists, text = await is_username_exists(username)
    print(is_exists, text)
    if is_exists:
        await message.answer(text)
        return
    await message.answer(text)
    
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
    """Подтверждение данных указанных во время Регистрации"""
    
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    
    # post запрос к созданию нового юзера
    state_data = await state.get_data()
    
    user_data = {
        "username": state_data.get("username"),
        "password": state_data.get("password"),
        "first_name": state_data.get("name"),
        "email": state_data.get("email"),
        "telegram_id": call.from_user.id,
        "main_language": state_data.get("language"),
    }
    
    is_create, service_msg = await create_user(user_data)
    if is_create:
        await call.answer('OK')
        await call.message.answer(
            f'Благодарю за регистрацию, {user_data.get('username')}. Ваши данные успешно сохранены!')
    else:
        await call.message.answer(service_msg)
        return
    
    await state.clear()


# запускаем анкету сначала
@questionnaire_router.callback_query(F.data == 'incorrect', Form.check_state)
async def questionnaire_check_state(call: CallbackQuery, state: FSMContext):
    """Отказ сохранять данные, указанные во время Регистрации. Регистрация идет по новой"""
    
    await call.answer('Видимо что-то напутали, давай по-новой!')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Последовательность вопросов анкеты ты помнишь, начнем с имени:')
    await state.set_state(Form.name)


@dp.message(F.text == "/start")
async def start_handler(message: Message, state: FSMContext):
    """Тестовый хэндлер, приветствие нового пользователя"""
    
    await state.clear()
    if message.from_user.id not in (459483895, 240753763):
        await message.answer('Ошибка доступа')
    else:
        print('Зашел в start_handler')
        print(message.chat.id)
        print(message.chat.username)
        async with ChatActionSender.typing(bot=bot, chat_id=message.chat.id):
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


@dp.message(Command("profile"))
async def profile_checking(message: Message, state: FSMContext):
    """Информация о профиле + 2 кнопки: редактировать и удалить"""
    
    await state.clear()
    curr_telegram_id = message.from_user.id
    profile_data = await get_profile_by_telegram_id(curr_telegram_id)
    print(profile_data)
    text = ''
    if "service message" in profile_data:
        text = profile_data.get("service message")
    else:
        for k, v in profile_data.items():
            text += f"{str(k)}: {str(v)} \n"
            print(k, v)
    await message.answer(text, reply_markup=edit_delete_profile_kb())  # inline кнопки


@dp.callback_query(F.data == "edit_profile")
async def edit_profile(call: CallbackQuery, state: FSMContext):  # <------ надо ли передавать state если не используется
    """Профиль -> Отработка кнопки Редактировать"""
    
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    await call.message.answer('Выбери, что поменять:', reply_markup=edit_kb())  # inline кнопки


# универсальный хэндлер
@edit_profile_router.callback_query(
    lambda new_callback: new_callback.data in ('edit_username', 'edit_password',
                                               'edit_first_name', 'edit_email',
                                               'edit_main_language'))
async def edit_profile_field(call: CallbackQuery, state: FSMContext):
    """Основной хэндлер, ловит callback от кнопок в разделе редактирования профиля
    Профиль -> Редактирование -> 'edit_username', 'edit_password', 'edit_first_name', 'edit_email', 'edit_main_language'
    Включает соответствующее FSM, передает в state.update_data текущее поле для работы с ним в хэндлере-обработчике
    """
    
    field_mapping = {
        'edit_username': {'prompt': 'Введи новый username', 'state': EditProfile.username, 'field': 'username'},
        'edit_password': {'prompt': 'Введи новый password', 'state': EditProfile.password, 'field': 'password'},
        'edit_first_name': {'prompt': 'Введи новое имя', 'state': EditProfile.first_name, 'field': 'first_name'},
        'edit_email': {'prompt': 'Введи новый email', 'state': EditProfile.email, 'field': 'email'},
        'edit_main_language': {'prompt': 'Введи новый language', 'state': EditProfile.main_language,
                               'field': 'main_language'},
    }
    field_info = field_mapping.get(call.data)
    
    if field_info:
        await state.update_data(field=field_info['field'])
        await state.set_state(field_info['state'])
        await call.message.answer(field_info['prompt'], reply_markup=None)
        print(f"Врубил {field_info['state']}")
    await call.message.edit_reply_markup(reply_markup=None)


async def is_edit_profile_state(message: Message, state: FSMContext) -> bool:
    """Кастомный фильтр для хэндлера process_field_input
    определяет, соответствует ли текущее FSM состояниям,
    в которые переходит бот после нажатия на кнопку редактирования
    если да, то возвращает True, и хэндлер отрабатывает
    """
    
    print("отработал is_edit_profile_state")
    return (await state.get_state()) in {
        EditProfile.username.state,
        EditProfile.password.state,
        EditProfile.first_name.state,
        EditProfile.email.state,
        EditProfile.main_language.state,
    }


@edit_profile_router.message(F.text, is_edit_profile_state)
# Дописать фильтр обработчик состояний
async def process_field_input(message: Message, state: FSMContext):
    """Обработка полученных от пользователя данных по редактированию профиля"""
    
    print(f"{'*' * 50} \nЗашел в process_field_input")
    state_data = await state.get_data()
    current_state = await state.get_state()
    field_name = state_data.get('field')
    field_value = message.text
    
    user_data = {"telegram_id": message.from_user.id, field_name: field_value}
    print(f"данные для обновления: {user_data}\n")
    
    is_updated, service_msg = await update_user_data(user_data, field_name)
    if is_updated:
        await message.answer('Данные обновлены')
    else:
        await message.answer(service_msg)
    """Возможно стоит добавить кнопки с выбором языка, кнопку юзернейм из телеграма если он != текущему
        Так же надо добавить нормальное добавление пароля, не как текст
    """


@dp.callback_query(F.data == "delete_profile")
async def edit_profile(call: CallbackQuery, state: FSMContext):
    """Профиль -> Отработка кнопки Удалить"""
    
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    await call.message.answer('Функция будет доступна в течении нескольких дней')


dp.include_router(questionnaire_router)
dp.include_router(edit_profile_router)


async def main():
    await set_default_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
 