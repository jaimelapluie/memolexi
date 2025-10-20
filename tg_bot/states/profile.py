from aiogram.fsm.state import State, StatesGroup


class Form(StatesGroup):
    name = State()
    language = State()
    username = State()
    email = State()
    password = State()
    check_state = State()


class EditProfile(StatesGroup):
    edit_mode = State()
    username = State()
    password = State()
    first_name = State()
    email = State()
    main_language = State()


class DeleteProfile(StatesGroup):
    delete_mode = State()
    

class AuthStates(StatesGroup):
    login_password = State()
