import httpx
from tg_bot.database.models import User
import peewee as pw
from tg_bot.database.models import User
from tg_bot.services.api_users import get_existing_token


async def get_words():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        return response.json()["results"]


async def get_users_words(user_id: int, page: int = 0, page_size: int = 5) -> tuple[bool, list[dict] | str]:
    async with httpx.AsyncClient() as client:
        print('> зашел в get_users_words')
        
        is_success, access_token = await get_existing_token(user_id)
        if is_success:
            url = "http://127.0.0.1:8000/words/"
            headers = {"Authorization": f"Bearer {access_token}"}
            print(headers)
        else:
            return False, 'в get_users_words токен не был получен'
        
        try:
            response = await client.get(url=url, headers=headers)
            # response = await client.get(url=url)
            print(response.text)
            response.raise_for_status()
            print('получил слова')
            return True, response.json()["results"]
        
        except httpx.HTTPStatusError as err:
            error_data = err.response.json()
            error_msg = error_data.get("detail", "Неизвестная ошибка")
            print('ошибка получения слов')
            return False, error_msg
            

# TODO: посмотреть какой тип (token)
async def create_word(word_data: dict, access_token: str) -> tuple[bool, str | None]:
    """Функция по взаимодействию с API, направляются запрос на создание карточки слова для пользователя"""
    
    print('Зашел в create_word')
    
    # отправка данных на API и получение ответа
    async with httpx.AsyncClient() as client:
        print('service -> create_word', word_data)
        print(access_token, type(access_token))
        url = "http://127.0.0.1:8000/words/"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = await client.post(url=url, json=word_data, headers=headers)
            status_code = response.status_code
            print(status_code)
            print(response)
            response.raise_for_status()
            return True, None
        
        except httpx.HTTPStatusError as err:
            try:
                print('.....')
                error_data = err.response.json()
                error_msg = error_data.get("detail", "Неизвестная ошибка")
                if not isinstance(error_msg, str):
                    error_msg = str(error_msg)
            except httpx.HTTPStatusError:
                error_msg = "Ошибка обработки ответа API"
            except Exception:
                error_msg = "Иная ошибка обработки ответа API"
            return False, error_msg
        
        except httpx.HTTPError as err:
            return False, f"Ошибка соединения с API: {str(err)}"
        