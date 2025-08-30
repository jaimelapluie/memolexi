from aiogram.fsm.state import State, StatesGroup


class AddWordProces(StatesGroup):
    waiting_word = State()
    waiting_translation = State()
    waiting_example = State()
    waiting_source = State()
    waiting_part_of_speech = State()
    waiting_picture = State()
    waiting_check_state = State()
    