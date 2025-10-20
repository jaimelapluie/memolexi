import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.chat_action import ChatActionSender
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tg_bot.config import bot_instance
from tg_bot.keyboards.profile_kb import language_kb, get_login_tg_kb, check_data_kb
from tg_bot.services.api_users import is_username_exists, create_user, get_profile_by_telegram_id
from tg_bot.states.profile import Form

questionnaire_router = Router()


# TODO: рефакторить код, убрать дублирующиеся фрагменты
@questionnaire_router.message(Command('start_questionnaire'))
async def start_questionnaire_process(message: Message, state: FSMContext):
    print('A')
    await state.clear()
    is_exists, data = await get_profile_by_telegram_id(message.from_user.id)
    if is_exists:
        await message.answer('По вашему telegram id профиль уже зарегистрирован. '
                             'Чтобы просмотреть его нажми команду: /profile')
        return
    
    async with ChatActionSender.typing(bot=bot_instance, chat_id=message.chat.id):
        await asyncio.sleep(0.5)
        await message.answer('Привет, для удобства и возможности доступа к сервису вне пределах telegram, '
                             'заполни анкету из 5 пунктов. Для начала напиши своё имя - как к тебе обращаться: ')
    await state.set_state(Form.name)


@questionnaire_router.message(F.text, Form.name, ~F.text.startswith('/'))
async def questionnaire_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    async with ChatActionSender.typing(bot=bot_instance, chat_id=message.chat.id):
        await asyncio.sleep(0.5)
        await message.answer(f'Приятно познакомиться, {message.text}! А какой основной язык ты сейчас учишь?',
                             reply_markup=language_kb())
    await state.set_state(Form.language)


@questionnaire_router.message((F.text.lower().contains('английский') | F.text.lower().contains('eng') |
                               F.text.lower().contains('english') |
                               F.text.lower().contains('испанский') | F.text.lower().contains('esp') |
                               F.text.lower().contains('espanol')), Form.language, ~F.text.startswith('/'))
async def questionnaire_language(message: Message, state: FSMContext):
    await state.update_data(language=message.text)
    await message.answer('Инфа принята!', reply_markup=ReplyKeyboardRemove())
    async with ChatActionSender.typing(bot=bot_instance, chat_id=message.chat.id):
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
@questionnaire_router.callback_query(F.data, Form.username, ~F.text.startswith('/'))
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
@questionnaire_router.message(F.text, Form.username, ~F.text.startswith('/'))
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


@questionnaire_router.message(F.text, Form.email, ~F.text.startswith('/'))
async def questionnaire_email(message: Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.answer('Ну и последнее: укажи свой password:')
    await state.set_state(Form.password)


@questionnaire_router.message(F.text, Form.password, ~F.text.startswith('/'))
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
@questionnaire_router.callback_query(F.data == 'correct', Form.check_state, ~F.text.startswith('/'))
async def questionnaire_submit_ok(call: CallbackQuery, state: FSMContext):
    """Подтверждение корректности введенных данных, указанных во время регистрации"""
    
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
@questionnaire_router.callback_query(F.data == 'incorrect', Form.check_state, ~F.text.startswith('/'))
async def questionnaire_submit_retry(call: CallbackQuery, state: FSMContext):
    """Отказ сохранять данные, указанные во время Регистрации. Регистрация пойдет по новой"""
    
    await call.answer('Видимо что-то напутали, давай по-новой!')
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer('Последовательность вопросов анкеты ты помнишь, начнем с имени:')
    await state.set_state(Form.name)
    