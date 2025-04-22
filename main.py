import logging
import os
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
import asyncio

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(name)  # Исправлено: name вместо name

# Инициализация бота
bot = Bot(token=os.getenv("7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"), parse_mode=ParseMode.HTML)  # Токен из переменной окружения
dp = Dispatcher()
router = Router()
dp.include_router(router)

# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    logger.info(f"Команда /start от {message.from_user.id}")
    await message.answer(f"Привет, {message.from_user.first_name}! Бот работает.")

# Запуск бота
async def main():
    logger.info("Бот запускается...")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")
    finally:
        await bot.session.close()

if name == "main":
    asyncio.run(main())
