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


async def get_token(user_data: dict) -> Tuple[bool, str]:
    """
    Асинхронно запрашивает токен аутентификации через DRF API
    
    Args - user_data (dict): Данные пользователя, содержащие username и password.
    
    Returns - Tuple[bool, str]: Кортеж, где первый элемент bool (получен ли токен? True/False),
    а второй элемент строка с токеном или сообщение об ошибке.
    
    Raises - ValueError: Если переданные данные пользователя некорректны или отсутствуют.
    
    ConnectionError: Если не удалось установить соединение с API.
    """
    
    url = "http://127.0.0.1:8000/auth/token/"
    
    try:
        async with httpx.AsyncClient() as client:
            try:
                print('Пробую...')
                response = await client.post(url, json=user_data)
                response.raise_for_status()
                token = response.json()
                print(f"token = {token}")
                return True, token
            
            except httpx.HTTPStatusError as err:
                print('get_token, A')
                error_msg = err.response.json().get("detail", "Неизвестная ошибка")
                
            except Exception as err:
                print('get_token, B')
                error_msg = err
                
    except Exception as err:
        print('get_token, C')
        error_msg = err
        
    print('get_token, D')
    return False, error_msg

    
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


async def update_user_data(user_data, field_name):
    """Функция обновляющая данные пользователя из данных переданных из хэндлера редактируемого"""
    
    url = f"http://127.0.0.1:8000/users/update/?telegram_id={user_data["telegram_id"]}"
    
    async with httpx.AsyncClient() as client:
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


async def api_delete_profile(token: dict) -> Tuple[bool, str | None]:
    """Асинхронно удаляет профиль пользователя через DRF API.

    Args:
        token (dict): Токен аутентификации пользователя (Bearer token).
    
    Returns:
        Tuple[bool, Optional[str]]: Кортеж, где первый элемент — успех операции
            (True — профиль удалён, False — ошибка), второй элемент — сообщение об
            ошибке или None при успешном удалении.
    
    Raises:
        ValueError: Если токен пустой или некорректный.
        httpx.HTTPError: Если произошла ошибка при выполнении запроса к API.
    """
    
    access_token = token.get('access')
    if not access_token or not isinstance(access_token, str):
        return False, "Токен должен содержать непустой ключ 'access' типа строки"
    
    url = f"http://127.0.0.1:8000/users/delete/"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    async with httpx.AsyncClient() as client:
        print(f"{'*' * 50}\nОтрабатывается непосредственное удаление")
        try:
            response = await client.delete(url=url, headers=headers)
            response.raise_for_status()
            return True, None
        
        except httpx.HTTPStatusError as err:
            try:
                error_data = await err.response.json()
                error_msg = error_data.get("detail", "Неизвестная ошибка")
                if not isinstance(error_msg, str):
                    error_msg = str(error_msg)
            except Exception:
                error_msg = "Ошибка обработки ответа API"
            return False, error_msg
        
        except httpx.HTTPError as err:
            return False, f"Ошибка соединения с API: {str(err)}"
        

async def get_profile_by_telegram_id(telegram_id) -> Tuple[bool, dict]:
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
            return True, data
            
        except httpx.HTTPStatusError as err:
            error_msg = err.response.json().get("service message")
            print(error_msg)
            return False, {'error_msg': error_msg}
