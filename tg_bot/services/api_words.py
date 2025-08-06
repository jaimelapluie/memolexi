import httpx


async def get_words():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        return response.json()["results"]


async def get_words_for_user(user_id: int, page: int, page_size: int) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/words/")
        
        return response.json()["results"]
    