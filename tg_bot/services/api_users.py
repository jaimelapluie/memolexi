import datetime
from typing import Tuple
import httpx
# from aiogram.fsm.context import FSMContext
from tg_bot.database.models import User
# from tg_bot.bot import EditProfile
import asyncio


# TODO: подумать над объединением с get_token
async def get_existing_token(telegram_id: int):
    """Функция получения токена из локальной БД - для бота"""
    
    token_or_none = User.get_or_none(User.telegram_id == telegram_id)
    print(f"\n зашел в get_existing_token, работаем с tg_id={telegram_id}")
    
    # запись с токеном в целом есть
    if token_or_none:
        now = datetime.datetime.now()
        
        # проверка, что access_token ещё действует с запасом в 10 секунд - на выполнение запроса
        # TODO: ++++ а что если запись есть и просрочено не только access_token, но и refresh_token?
        if token_or_none.token_expiry >= now + datetime.timedelta(seconds=10):
            access_token = token_or_none.access_token
            print(f"access_token получен: {access_token}")
            return True, access_token
        
        # в случае просрочки токена, его следует обновить
        else:
            print('get_existing_token токен просрочен пробую обновить..')
            is_updated, token_or_err = await update_token({'refresh': token_or_none.refresh_token})
            # TODO: перенести блок put_token_to_local_db внутрь  update_token
            if is_updated:
                print('новый токен получен')
                is_exist, user_data = await get_profile_by_telegram_id(telegram_id=telegram_id)
                if is_exist:
                    username = user_data.get('username')
                    user_data = dict(telegram_id=telegram_id, username=username)
                    
                    # TODO: проверку добавить, что токен записался в локал БД
                    is_done = await put_token_to_local_db(token_or_err, user_data)
                    if is_done:
                        access_token = token_or_err.get('access')
                        print('токен получен и сохранен в БД')
                        return True, access_token
                    return False, 'put_token_to_local_db: в базу не сохранилось'
                else:
                    return False, "get_existing_token: Пользователь не зарегистрирован"
                
            return False, token_or_err

    return False, "Токен должен содержать непустой ключ 'access' типа строки"
    

# TODO: оптимизировать?
async def put_token_to_local_db(token_data, user_data):
    """Полученные токены сохраняет в локальную БД.
    Если такой telegram_id существует, то перезаписывает?"""
    
    def sync_db_operation():
        print('Зашел в put_token_to_local_db')
        access_token = token_data['access']
        refresh_token = token_data['refresh']
        
        now = datetime.datetime.now()
        # TODO: дублируются настройки. Отдельный хендлер, для автоматизации получения данных настроек?
        token_expiry = now + datetime.timedelta(minutes=45)  # setting ->'ACCESS_TOKEN_LIFETIME': timedelta(minutes=45)
        print('token_expiry:', token_expiry)
    
        try:
            telegram_id = user_data['telegram_id']
            user_data_db = dict(
                username=user_data['username'],
                access_token=access_token,
                refresh_token=refresh_token,
                token_expiry=token_expiry)
            print('user_data=', user_data_db)
            user, created = User.get_or_create(telegram_id=telegram_id, defaults=user_data_db )
            print('user, created=', user, created)
            if not created:
                print('вошел в if not created:')
                User.update(**user_data_db).where(User.telegram_id == telegram_id).execute()
            return True
        except Exception as e:
            print('put_token_to_local_db Ошибка:', repr(e))
            # traceback.print_exc()
            return False
    
    return await asyncio.to_thread(sync_db_operation)


async def update_token(token: dict) -> Tuple[bool, str | dict]:
    # TODO: дописать документацию
    
    url = "http://127.0.0.1:8000/auth/token/refresh/"
    
    async with httpx.AsyncClient() as client:
        try:
            print(f'Пробую обновить токен... при помощи {token}')
            response = await client.post(url=url, json=token)
            print(response.status_code)
            print(response.text)
            response.raise_for_status()
            refreshed_token = response.json()
            return True, refreshed_token
        
        except httpx.HTTPStatusError as err:
            print('refresh_token, A')
            try:
                error_msg = err.response.json().get("detail", "Неизвестная ошибка")
            except:
                error_msg = err.response.text
            
        except Exception as err:
            print('refresh_token, B')
            error_msg = err
            
    return False, error_msg
    

# TODO: надо дописать возможность обновления токена и подумать над объединением с get_existing_token
#  Хорошая идея - get_token общая функция, перед обращением к API она сначала смотрит в локальной
#  БД, и если не находит делает запрос к API, а после получения - сохраняет в локальную БД!
async def get_token(user_data: dict) -> Tuple[bool, str]:
    """
    Асинхронно запрашивает токен аутентификации через DRF API
    
    Args - user_data (dict): Данные пользователя, содержащие username и password.
    
    Returns - Tuple[bool, str]: Кортеж, где первый элемент bool (получен ли токен? True/False),
    а второй элемент строка с токеном или сообщение об ошибке.
    
    Raises - ValueError: Если переданные данные пользователя некорректны или отсутствуют.
    
    ConnectionError: Если не удалось установить соединение с API.
    """
    print('\n> Зашел в get_token')
    
    url = "http://127.0.0.1:8000/auth/token/"
    
    try:
        async with httpx.AsyncClient() as client:
            try:
                print('Пробую получить токен...')
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


async def update_user_data(user_data, field_name):  # Добавить токен доступа
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
        

# TODO: add token verification! Now an access is free by telegram_id
async def get_profile_by_telegram_id(telegram_id) -> Tuple[bool, dict]:
    """Функция возвращает информацию о профиле"""
    
    url = f"http://127.0.0.1:8000/users/check_telegram_id/?telegram_id={telegram_id}"
    print(f"\n get_profile_by_telegram_id работает по ссылке {url}")
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
