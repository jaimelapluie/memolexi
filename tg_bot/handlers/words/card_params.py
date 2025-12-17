from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from tg_bot.keyboards.profile_kb import get_language_kb
from tg_bot.keyboards.words_kb import get_dynamic_add_word_kb
from tg_bot.services.api_users import update_user_data

card_params_router = Router()


@card_params_router.callback_query(F.data == 'change_language')
async def handle_change_language(call: CallbackQuery, state: FSMContext, token):
    """
    Хэндлер отрабатывает callback полученный из get_dynamic_add_word_kb, вызванной в handle_add_word_command.
    Хэндлер редактирует сообщение с просьбой ввести слово, и вместо текущего языка просит выбрать новый язык,
    а так же показывает клавиатуру с перечнем языков.
    """
    
    print('\nЗашел в handle_change_language')
    await call.message.edit_text(text='Введите новое слово или выражение:\n'
                                      '(выберите желаемый язык)', reply_markup=await get_language_kb())


@card_params_router.callback_query(lambda new_callback: str(new_callback.data).startswith('language_code='))
async def handle_change_language1(call: CallbackQuery, state: FSMContext, token):
    """
    Хэндлер используется во время сценария добавления нового слова, а именно при смене языка.
    Хэндлер перехватывает callback от нажатия на кнопку клавиатуры get_language_kb после выбора языка (предыдущий шаг).
    Применяет изменения и вносит их в БД в таблицу User поле main_language.
    Хэндлер редактирует сообщение с просьбой ввести слово, и вместо просьбы выбрать новый язык отображает выбранный,
    а так же показывает клавиатуру get_dynamic_add_word_kb из изначального хэндлера handle_add_word_command.
    """
    
    print('\nЗашел в handle_change_language1')

    field_name = 'language_code'
    language_code = call.data.split('&')[0].split('=')[1]
    language = call.data.split('&')[1].split('=')[1]
    
    user_data = {"telegram_id": call.from_user.id, field_name: language_code}
    print(f"данные для обновления: {user_data}\n")
    
    is_updated, service_msg = await update_user_data(user_data, field_name)
    if is_updated:
        await call.message.edit_text(text=f'Введите новое слово или выражение:\n(выбранный язык - {language})',
                                     reply_markup=await get_dynamic_add_word_kb(state))
    else:
        await call.message.edit_text(text=f'Введите новое слово или выражение:\n(ошибка выбора языка!)',
                                     reply_markup=await get_dynamic_add_word_kb(state))
    