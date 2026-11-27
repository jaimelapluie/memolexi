import httpx


async def get_languages_list() -> tuple[bool, list[dict] | str]:
    """Направляет запрос к API MemoLexi для получения перечня языков"""
    print('\n> (API) зашел в bot get_languages_list  ', end=' ')
    
    async with httpx.AsyncClient() as client:
        try:
            url = "http://127.0.0.1:8000/references/languages/"
            response = await client.get(url=url)
            response.raise_for_status()
            print('получил перечень языков: ', end='')
            print(response.json())
            return True, response.json()
        
        except httpx.HTTPStatusError as err:
            try:
                error_data = err.response.json()
                error_msg = (
                    error_data.get("detail", "Неизвестная ошибка")
                    if isinstance(error_data, dict)
                    else str(error_data)
                )
            except ValueError:
                error_msg = err.response.text or f"HTTP ошибка {err.response.status_code}"
            
            print("Ошибка API при получении языков (%s): %s", err.response.status_code, error_msg)
            return False, error_msg
        
        except httpx.RequestError as err:
            print("Сетевая ошибка при обращении к API MemoLexi")
            return False, f"API MemoLexi не отвечает: {err}"
