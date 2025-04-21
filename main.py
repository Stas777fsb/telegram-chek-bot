mport os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram import F

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer("Привет! Бот работает!")

async def main():
    await dp.start_polling(bot)

if name == "main":
    asyncio.run(main())
