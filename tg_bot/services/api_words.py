import httpx
from tg_bot.database.models import User
import peewee as pw
from tg_bot.database.models import User


async def get_words():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        return response.json()["results"]


async def get_words_for_user(user_id: int, page: int, page_size: int) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        
        return response.json()["results"]


# TODO: посмотреть какой тип (token)
async def create_word(word_data: dict, access_token: str) -> tuple[bool, str | None]:
    """Функция по взаимодействию с API, направляются запрос на создание карточки слова для пользователя"""
    
    print('Зашел в create_word')
    
    # отправка данных на API и получение ответа
    async with httpx.AsyncClient() as client:
        print('service -> create_word', word_data)
        print(access_token, type(access_token))
        # TODO: посмотреть как из token достать  access_token
        url = "http://127.0.0.1:8000/words/"
        headers = {"Authorization": f"Bearer {access_token}"}

        try:
            response = await client.post(url=url, json=word_data, headers=headers)
            response.raise_for_status()
            print(response)
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
        