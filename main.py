import os
import asyncio
import random
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from collections import defaultdict
from datetime import datetime

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище баланса
user_balances = defaultdict(lambda: 0.00)

# Хранилище бесплатных IP-проверок
user_check_limits = {}

# Главное меню
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="Проверка IP")],
        [KeyboardButton(text="Проверка номера телефона")],
        [KeyboardButton(text="Проверка email")],
        [KeyboardButton(text="Пополнить баланс")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Команда /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    balance = user_balances[user_id]
    await message.answer(
        f"<b>Добро пожаловать!</b>\n\n"
        f"Ваш ID: <code>{user_id}</code>\n"
        f"Баланс: <b>${balance:.2f}</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

# Кнопка "Проверка IP"
@dp.message(F.text == "Проверка IP")
async def ask_for_ip(message: Message):
    await message.answer("Пожалуйста, отправьте IP-адрес для проверки.")

# Обработка IP (формат IPv4)
@dp.message(F.text.regexp(r"^\d{1,3}(\.\d{1,3}){3}$"))
async def check_ip(message: Message):
    user_id = message.from_user.id
    today = datetime.utcnow().date()

    if user_id not in user_check_limits or user_check_limits[user_id]["date"] != today:
        user_check_limits[user_id] = {"date": today, "count": 0}

    if user_check_limits[user_id]["count"] >= 10:
        await message.answer("Лимит бесплатных IP-проверок на сегодня исчерпан. Каждая следующая проверка стоит $0.10.")
        return

    user_check_limits[user_id]["count"] += 1
    ip = message.text.strip()
    risk_score = random.randint(0, 100)  # Заглушка, потом подключим API

    await message.answer(
        f"<b>IP:</b> <code>{ip}</code>\n"
        f"<b>Риск:</b> {risk_score}%\n"
        f"(демонстрационные данные, позже будет подключена реальная проверка)",
        parse_mode="HTML"
    )

# Остальные кнопки-заглушки
@dp.message(F.text == "Проверка номера телефона")
async def handle_check_phone(message: Message):
    await message.answer("Функция проверки номера телефона скоро будет доступна.")

@dp.message(F.text == "Проверка email")
async def handle_check_email(message: Message):
    await message.answer("Функция проверки email скоро будет доступна.")

@dp.message(F.text == "Пополнить баланс")
async def handle_topup(message: Message):
    await message.answer("Выберите способ пополнения: BTC или LTC.\n(Детали будут добавлены позже)")

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
