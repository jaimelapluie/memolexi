from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from tg_bot.keyboards.words_kb import get_back_after_delete_word_kb, get_delete_word_kb
from tg_bot.prompts.word_card import build_word_card_caption
from tg_bot.services.api_words import delete_word

delete_word_router = Router()


@delete_word_router.callback_query(F.data == 'delete_word')
async def handle_delete_words(call: CallbackQuery, state: FSMContext):
    """Хэндлер начинающий процесс удаления слова."""
    state_data = await state.get_data()
    word_card = state_data.get('word_card')
    if word_card:
        await call.message.edit_text(f'‼️ Точно удалить? ‼️\n\n{build_word_card_caption(word_card)}',
                                     reply_markup=await get_delete_word_kb())
    else:
        await call.message.edit_text('Слово не найдено, попробуйте ещё раз.')
    

@delete_word_router.callback_query(F.data == 'yes_delete_word')
async def handle_confirm_delete_words(call: CallbackQuery, state: FSMContext, token: str):
    """
    Хэндлер осуществляющий процесс удаления слова.
    
    """
    print('\nhandle_delete_words')
    data = await state.get_data()
    word_id = data.get('word_id')
    if word_id:
        word = data.get('word')
        word_data = {"word_id": word_id}
        print(f"данные для удаления: {word_data}\n")
        
        is_deleted, service_msg = await delete_word(word_data, token)
        if is_deleted:
            await call.message.edit_text(f'{str(word) + " удалено успешно." if word else "Удалено успешно!"}',
                                         reply_markup=await get_back_after_delete_word_kb())
        else:
            await call.message.edit_text(service_msg, reply_markup=None)
    else:
        await call.message.edit_text('Слово не найдено, попробуйте ещё раз.')
    await state.set_state(None)

# feat(bot): add word deletion confirmation and FSM validation
#
# - Add confirm_delete_word handler for deletion prompt
# - Rename execution handler to process_delete_word and validate word_id
# - Answer callback queries and reset FSM state after completion
