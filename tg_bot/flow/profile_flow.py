from aiogram.fsm.context import FSMContext

from tg_bot.services.api_users import get_profile_by_telegram_id, update_user_data


async def get_profile_and_sync_state(
    telegram_id,
    state: FSMContext
) -> tuple[bool, dict | None | str]:
    """
    Пробует получить профиль из FSM, иначе пробует получить через API MemoLexi и синхронизирует profile_data в FSM.
    Используется в сценариях просмотра или редактирования профиля.
    """
    
    print(f'\n\nget_profile_and_sync_state')
    
    state_data = await state.get_data()
    profile_data = state_data.get('profile_data')
    
    if profile_data:
        return True, profile_data
    
    is_exists, profile_data = await get_profile_by_telegram_id(telegram_id)
    if is_exists:
        print(f'{is_exists=} {profile_data=}')
        await state.update_data(profile_data=profile_data)
    
    return is_exists, profile_data


async def update_user_data_and_sync_state(user_data, field_name, state: FSMContext) -> tuple[bool, dict | None | str]:
    """
    Пробует получить профиль из FSM, иначе пробует получить через API MemoLexi и синхронизирует profile_data в FSM.
    Используется в сценариях просмотра или редактирования профиля.
    """
    
    print(f'>>>> update_user_data_and_sync_state')
    is_updated, profile_data_or_error = await update_user_data(user_data, field_name)
    
    if is_updated:
        profile_data = profile_data_or_error
        await state.update_data(profile_data=profile_data)  # обновляю данные FSM из API
        return True, None
    else:
        error_message = profile_data_or_error
        return False, error_message
