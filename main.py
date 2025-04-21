import os
from aiogram import Bot

BOT_TOKEN = os.getenv("BOT_TOKEN")  # Получаем из переменных окружения
bot = Bot(token=BOT_TOKEN)
