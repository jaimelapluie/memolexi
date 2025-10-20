from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from tg_bot.keyboards.words_kb import check_data_kb, get_dynamic_add_word_kb
from tg_bot.services.api_users import get_profile_by_telegram_id, get_existing_token, get_token, put_token_to_local_db
from tg_bot.services.api_words import create_word
from tg_bot.states.profile import AuthStates
from tg_bot.states.words import AddWordProces


adding_words_router = Router()

STATE_CONFIG = {
    AddWordProces.waiting_word: {
        "data_key": "word",
        "prompt": "Введите новое слово или выражение:",
        "next_state": AddWordProces.waiting_translation,
        "word_or_expression": lambda text: "выражения" if len(text.split()) > 1 else "слова"
    },
    # TODO: если слово не указано выводится некорректное сообщение - ..'слова, которое вы введете позже' ""
    AddWordProces.waiting_translation: {
        "data_key": "translation",
        "prompt": lambda data: f'Введите перевод для '
                               f'{data.get('word_or_expression', 'слова, которое вы введете позже')} '
                               f'"{data.get('word', '')}"',
        "next_state": AddWordProces.waiting_example,
    },
    AddWordProces.waiting_example: {
        "data_key": "example",
        "prompt": lambda data: f'Введите пример использования для '
                               f'"{data.get("word", 'слова, которое вы введете позже')}"',
        "next_state": AddWordProces.waiting_source,
    },
    AddWordProces.waiting_source: {
        "data_key": "source",
        "prompt": lambda data: f'Откуда взято это {data.get("word_or_expression", "")}- книга, сериал, статья?',
        "next_state": AddWordProces.waiting_part_of_speech,
    },
    AddWordProces.waiting_part_of_speech: {
        "data_key": "part_of_speech",
        "prompt": "Для удобства можно указать часть речи:",
        "next_state": AddWordProces.waiting_check_state,
     }
}


# TODO в handlers/profile/delete есть такая же функция. Объединить
@adding_words_router.message(AuthStates.login_password, ~F.text.startswith('/'))
async def handle_login_and_save_token(message: Message, state: FSMContext):
    """Отрабатывет для получения токена"""
    
    print('\n Отрабатывает handle_login_and_save_token ')
    await message.answer("handle_login_and_save_token: пробуем получить токен")

    telegram_id = message.from_user.id
    password = message.text
    is_exist, data = await get_profile_by_telegram_id(telegram_id=telegram_id)
    if is_exist:
        print('get_profile_by_telegram_id получил профиль:', data)
        username = data.get("username")
    else:
        return await message.answer("Пользователь не найден")

    user_data = {"username": username, "password": password}
    is_success, auth_token = await get_token(user_data)

    if is_success:
        print(f"auth_token: {auth_token}")
        await message.answer(f"Пароль верный. Успешно получены токены")
        user_data.pop("password")
        user_data.update(telegram_id=telegram_id)

        is_done = await put_token_to_local_db(auth_token, user_data)
        if is_done:
            print("Врубаю AddWordProces.waiting_check_state")
            await state.set_state(AddWordProces.waiting_check_state)
            print("Врубил <<")
            await message.answer(text=f"Отлично, теперь вернемся к подтверждению действия по добавлению слова:",
                                 reply_markup=check_data_kb())
        else:
            await message.answer(text='В handle_login_and_save_token произошла ошибка. '
                                      'Токен не сохранен в локальную базу')
    else:
        await message.answer(f"Вероятно введен неверный пароль, повторите попытку")
    print("Завершение работы handle_login_and_save_token")


def make_caption(data):
    print('Зашел в сборщик caption для AddWordProces.waiting_check_state:', "*" * 50)
    caption = '\n'.join(
        f'{key}: {data.get(key, "—")}' for key in ("word", "translation", "example", "source", "part_of_speech")
    )
    caption = f'Проверь, всё ли корректно? \n\n{caption}'
    return caption


# TODO: Добавить проверку, что пользователь существует - что есть кому добавлять вообще
@adding_words_router.message(Command('add_word'))
async def handle_add_word_command(message: Message, state: FSMContext):
    """
    Начальный хэндлер, отрабатывающий команду add_word.
    Обращается к словарю STATE_CONFIG, извлекает текст и устанавливает состояние для FSM.
    """
    
    print('Пробую добавить новое слово')
    await state.clear()
    await state.set_state(AddWordProces.waiting_word)
    await message.answer(text=STATE_CONFIG[AddWordProces.waiting_word]['prompt'],
                         reply_markup=await get_dynamic_add_word_kb(state))


async def is_state_in_config(message: Message, state: FSMContext) -> bool:
    """Кастомный фильтр для хэндлера process_input.
    Определяет, соответствует ли текущее FSM состояние одному из STATE_CONFIG
    Если да, возвращает True, нет — False
    """
    return await state.get_state() in STATE_CONFIG
    

@adding_words_router.message(F.text, is_state_in_config)
async def process_word_input(message: Message, state: FSMContext):
    """
    Ключевой хэндлер перебора FSM-состояний по заполнению карточек слова.
    В зависимости от текущего состояния, FSM data пополняется новой информацией от пользователя:
    Словарь STATE_CONFIG содержит ожидаемые состояния и их конфигурации (ключевое слово, текст, и следующее состояние)
    Функция берет данные пользователя и добавляет их в качестве значения по ключу (из конфиги).
    
    Последние состояние (waiting_check_state) отрабатывается в отдельном условии, выводя собранную информацию,
    и направляя её на проверку пользователю - появляются кнопки ("Ок" и "Заполнить заново").
    После хэндлер передает управление к waiting_check_state
    
    :param message:
    :param state:
    :return:
    """
    current_state = await state.get_state()
    config = STATE_CONFIG[current_state]
    user_input = message.text
    
    # Обновление данных FSM
    if current_state == AddWordProces.waiting_word:
        word_or_expression = config["word_or_expression"](user_input)
        await state.update_data(word=user_input, word_or_expression=word_or_expression)
    else:
        await state.update_data(**{config['data_key']: user_input})
    data = await state.get_data()

    # Получение промпта для следующего состояния
    next_state = config["next_state"]
    if next_state == AddWordProces.waiting_check_state:
        caption = make_caption(data)  # получение текста вынесено в отдельную функцию
        await message.answer(text=caption, reply_markup=check_data_kb())
        await state.set_state(AddWordProces.waiting_check_state)
        return
        
    next_config = STATE_CONFIG.get(next_state, {})
    prompt = next_config.get('prompt', 'Проверьте корректность данных')
    if callable(prompt):
        prompt = prompt(data)
    
    await message.answer(text=prompt, reply_markup=await get_dynamic_add_word_kb(state))
    await state.set_state(next_state)


# TODO: ДОписать хэндлер
@adding_words_router.callback_query(F.data == 'save', is_state_in_config)
async def handle_save_state(call: CallbackQuery, state: FSMContext):
    print('Сохраняю состояние - заглушка')
    await call.message.answer('Сохраняю состояние - заглушка')


@adding_words_router.callback_query(F.data == 'skip', is_state_in_config)
async def handle_skip_state(call: CallbackQuery, state: FSMContext):
    """Handle 'skip' button press to skip current field in word card flow.

    Retrieves the current state, determines the next state using STATE_CONFIG,
    dynamically generates the caption and keyboard, and transitions to the next state.

    Args:
        call (CallbackQuery): The Telegram callback query object.
        state (FSMContext): The finite state machine context for managing states.

    Returns:
        None

    Notes:
        - Uses 'make_caption' function to generate captions for 'waiting_check_state'.
        - Dynamically generates keyboards via 'get_dynamic_add_word_kb' based on current data.
        - Removes previous reply markup before sending new message.
    """

    # Узнаю текущее состояние, и через STATE_CONFIG смотрю следующее состояние - next_state
    current_state = await state.get_state()
    current_config = STATE_CONFIG[current_state]
    next_state = current_config['next_state']
    data = await state.get_data()

    # Готовлю инфо-текст - какую информацию надо ввести для следующего состояние
    # выполняю проверку грядущего состояния. Для waiting_check_state особый текст
    if next_state == AddWordProces.waiting_check_state:
        next_prompt = make_caption(data)
        keyboard = check_data_kb()
    else:
        next_prompt = STATE_CONFIG[next_state]['prompt']
        keyboard = await get_dynamic_add_word_kb(state)
        if callable(next_prompt):
            next_prompt = next_prompt(data)

    # Вывожу подготовленный ранее инфо-текст для следующего состояния и включаю его
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=next_prompt, reply_markup=keyboard)
    await state.set_state(next_state)


@adding_words_router.callback_query(F.data == 'incorrect', AddWordProces.waiting_check_state)
async def handle_retry_state(call: CallbackQuery, state: FSMContext):
    print('incorrect')
    print('До', await state.get_data())
    await state.clear()
    await state.set_state(AddWordProces.waiting_word)
    print('После', await state.get_data())

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(text=STATE_CONFIG[AddWordProces.waiting_word]['prompt'],
                              reply_markup=await get_dynamic_add_word_kb(state))


@adding_words_router.callback_query(F.data == 'correct', AddWordProces.waiting_check_state)
async def handle_confirm_state(call: CallbackQuery, state: FSMContext):
    """Добавление карточки слова текущим пользователем в БД.
    Отрабатывает после подтверждения корректности введенных данных на этапе FSM.
    """
    print("Зашел в waiting_check_state_ok")
    # сбор данных
    state_data = await state.get_data()
    telegram_id = call.from_user.id
    word_data = {
        "word": state_data.get("word"),
        "translation": state_data.get("translation"),
        "example": state_data.get("example"),
        "source": state_data.get("source"),
        "part_of_speech": state_data.get("part_of_speech"),
    }
    
    # запрос токена из локальной БД
    is_token_exist, access_token = await get_existing_token(telegram_id)
    print("получил от get_existing_token(telegram_id) token=", access_token)
    if not is_token_exist:
        # токена нету, запрашиваю пароль
        await call.message.answer('Пожалуйста, введите пароль для добавления данных')
        await state.set_state(AuthStates.login_password)
        return
    
    # токен есть, пробуем создать запись в БД
    is_created, word = await create_word(word_data, access_token)
    if is_created:
        await call.message.answer(text=f"Успешно добавлено!")
        await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопки
        print('УРА! waiting_check_state_ok -> create_word -> добавлено')
        await state.clear()
    else:
        print('Слово не добавлено')
        await call.message.answer(text=word)

# TODO: handlers/adding_words.py — все message/callback хэндлеры
#  filters/is_state_in_config.py — кастомный фильтр.
#  services/words.py — логика работы с данными FSM.
#  utils/text.py — make_caption.
#  Все тексты (Введите слово, Проверь всё ли корректно) вынести в отдельный модуль/файл
#  Добавить логгирование
