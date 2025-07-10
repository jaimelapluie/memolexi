from aiogram import Router, types
from aiogram.filters import CommandStart
import httpx

router = Router()


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Давай учить слова?")

#
# @router.message(CommandStart())
# async def get_words(message: types.Message):
#     async with httpx.AsyncClient() as client:
#         response = await client.get("http://127.0.0.1:8000/words/")
#         return response.json()["results"]
