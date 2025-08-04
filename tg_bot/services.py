from typing import Any, Tuple
import httpx
# from aiogram.fsm.context import FSMContext

# from tg_bot.bot import EditProfile


async def get_words():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        return response.json()["results"]


async def get_words_for_user(user_id: int, page: int, page_size: int) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        
        return response.json()["results"]


async def create_user(user_data):
    """Функция создает нового пользователя из данных переданных при регистрации"""

    async with httpx.AsyncClient() as client:
        url = f"http://127.0.0.1:8000/users/"
        print('service -> create user', user_data)

        try:
            response = await client.post(url, json=user_data)
            print(response.status_code)
            response.raise_for_status()
            return True, None
        
        except httpx.HTTPStatusError as err:
            error_detail = err.response.json().get("detail", str(err))
            print(f'questionnaire_check_state except: Ошибка в создании юзера {error_detail}')
            return False, f'Ошибка в создании юзера: {error_detail}'


async def update_user_data(user_data, field_name):
    """Функция обновляющая данные пользователя из данных переданных из хэндлера редактируемого"""

    async with httpx.AsyncClient() as client:
        url = f"http://127.0.0.1:8000/users/update/?telegram_id={user_data["telegram_id"]}"
        print(f'{"*" * 50}\nвошел в update_user_data')
        try:
            response = await client.put(url, json=user_data)
            print('try'.endswith(''))
            response.raise_for_status()
            print(' отработал')
            return True, None
        
        except httpx.HTTPStatusError as err:
            print(' не отработал')
            print(f"Ошибка в update_user_data: {err.response.text}")
            print(f"err.response.json() {err.response.json()}")
            
            error_detail = f"{err.response.json().get(field_name)[0]}"
            print(f'error_detail -> {error_detail}')
            return False, error_detail

    
async def is_username_exists(username) -> tuple[bool, str]:
    """Функция проверяет существование в БД переданного username"""
    
    url = f"http://127.0.0.1:8000/users/check_username/?username={username}"
    print(f'Ищу вот по этой ссылке {url}')
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            print(f'data = {data}')
            if data.get("exists"):
                return True, f'username "{username}" уже существует, придумай другой'
            return False, f'username "{username}" — свободен'
        
        except httpx.HTTPError as err:
            text = f"Ошибка при запросе: {err}"
            print(text)
            return True, text


async def get_profile_by_telegram_id(telegram_id) -> dict:
    """Функция возвращает информацию о профиле"""
    
    url = f"http://127.0.0.1:8000/users/check_telegram_id/?telegram_id={telegram_id}"
    print(f"Работаю по ссылке {url}")
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            response.raise_for_status()  # <----- (1) вопрос разобран
            data = response.json()
            print(type(data))
            print("Выхожу из get_profile_by_telegram_id")
            return data
            
        except httpx.HTTPStatusError as err:
            text = (f"Ошибка: {err.response.json().get("service message")}. "
                    f"Чтобы посмотреть профиль, сначала его надо зарегистрировать:"
                    f" введи команду \n/start_questionnaire")
            print(text)
            return {'service message': text}


