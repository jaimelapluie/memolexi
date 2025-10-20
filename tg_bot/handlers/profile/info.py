from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from tg_bot.keyboards.profile_kb import get_edit_delete_profile_kb
from tg_bot.services.api_users import get_profile_by_telegram_id


info_profile_router = Router()


@info_profile_router.message(Command("profile"))
async def profile_checking(message: Message, state: FSMContext):
    """Информация о профиле + 2 кнопки: редактировать и удалить"""
    
    print("\nРаботает profile_checking")
    await state.clear()
    
    curr_telegram_id = message.from_user.id
    text = ''
    keyboard = None
    
    is_exists, data = await get_profile_by_telegram_id(curr_telegram_id)
    
    if is_exists:
        for k, v in data.items():
            text += f"{str(k)}: {str(v)} \n"
            print(k, v)
        keyboard = get_edit_delete_profile_kb()
    else:
        error_msg = data['error_msg']
        text = (f"Ошибка: {error_msg}. "
                f"Чтобы посмотреть профиль, сначала его надо зарегистрировать. "
                f"Введи команду: \n/start_questionnaire")
    await message.answer(text, reply_markup=keyboard)  # inline кнопки
    