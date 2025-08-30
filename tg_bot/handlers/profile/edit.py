from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from tg_bot.keyboards.profile_kb import get_edit_kb
from tg_bot.services.api_users import update_user_data
from tg_bot.states.profile import EditProfile


edit_profile_router = Router()


@edit_profile_router.callback_query(F.data == "edit_profile")
async def edit_profile(call: CallbackQuery, state: FSMContext):  # <------ надо ли передавать state если не используется
    """Профиль -> Отработка кнопки Редактировать"""
    
    await call.message.edit_reply_markup(reply_markup=None)  # удаляю кнопку
    await call.message.answer('Выбери, что поменять:', reply_markup=get_edit_kb())  # inline кнопки


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
    
    # Возможно стоит добавить кнопки с выбором языка, кнопку юзернейм из телеграма если он != текущему
    # Так же надо добавить нормальное добавление пароля, не как текст
    
    print(f"{'*' * 50} \nЗашел в process_field_input")
    state_data = await state.get_data()
    field_name = state_data.get('field')
    field_value = message.text
    
    user_data = {"telegram_id": message.from_user.id, field_name: field_value}
    print(f"данные для обновления: {user_data}\n")
    
    is_updated, service_msg = await update_user_data(user_data, field_name)
    if is_updated:
        await message.answer('Данные обновлены')
    else:
        await message.answer(service_msg)
    await state.set_state(None)
