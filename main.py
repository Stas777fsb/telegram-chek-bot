import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Хранилище баланса (в реальном проекте — база данных)
user_balances = defaultdict(lambda: 0.00)  # Стартовый баланс $0.00

# Клавиатура меню
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="Проверка IP")],
        [KeyboardButton(text="Проверка номера телефона")],
        [KeyboardButton(text="Проверка email")],
        [KeyboardButton(text="Пополнить баланс")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Обработка команды /start
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    balance = user_balances[user_id]
    text = (
        f"<b>Ваш ID:</b> <code>{user_id}</code>\n"
        f"<b>Баланс:</b> ${balance:.2f}\n\n"
        "Выберите действие:"
    )
    await message.answer(text, reply_markup=get_main_keyboard(), parse_mode="HTML")

# Заглушки для кнопок
@dp.message(lambda msg: msg.text == "Проверка IP")
async def handle_check_ip(message: Message):
    await message.answer("Функция проверки IP скоро будет доступна.")

@dp.message(lambda msg: msg.text == "Проверка номера телефона")
async def handle_check_phone(message: Message):
    await message.answer("Функция проверки номера телефона скоро будет доступна.")

@dp.message(lambda msg: msg.text == "Проверка email")
async def handle_check_email(message: Message):
    await message.answer("Функция проверки email скоро будет доступна.")

@dp.message(lambda msg: msg.text == "Пополнить баланс")
async def handle_topup(message: Message):
    await message.answer("Выберите способ пополнения:\nBTC или LTC (будет добавлено позже).")
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

# Хранилище бесплатных проверок (в памяти — потом можно в БД)
user_check_limits = {}

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Проверка IP")],
        [KeyboardButton(text="Проверка номера телефона")],
        [KeyboardButton(text="Проверка email")],
        [KeyboardButton(text="Пополнить баланс")]
    ],
    resize_keyboard=True
)
@dp.message(Command("start"))
async def start_handler(message: Message):
    user_id = message.from_user.id
    balance = 0.0  # Пока заглушка, позже добавим хранение баланса
    await message.answer(
        f"<b>Добро пожаловать!</b>\n\n"
        f"Ваш ID: <code>{user_id}</code>\n"
        f"Баланс: <b>${balance:.2f}</b>\n",
        reply_markup=main_menu
    )
   @dp.message(F.text == "Проверка IP")
async def ask_for_ip(message: Message):
    await message.answer("Пожалуйста, отправьте IP-адрес для проверки.")
@dp.message(F.text.regexp(r"^\d{1,3}(\.\d{1,3}){3}$"))
async def check_ip(message: Message):
    user_id = message.from_user.id
    today = datetime.utcnow().date()

    # Проверяем, сколько уже проверок сделал пользователь
    if user_id not in user_check_limits or user_check_limits[user_id]["date"] != today:
        user_check_limits[user_id] = {"date": today, "count": 0}

    if user_check_limits[user_id]["count"] >= 10:
        await message.answer("Лимит бесплатных IP-проверок на сегодня исчерпан. Стоимость каждой следующей: $0.10")
        return

    user_check_limits[user_id]["count"] += 1

    ip = message.text.strip()
    risk_score = random.randint(0, 100)  # Заглушка, потом заменим на API

    await message.answer(
        f"<b>IP:</b> <code>{ip}</code>\n"
        f"<b>Риск:</b> {risk_score}%\n"
        f"(данные демонстрационные — подключим реальную проверку позже)"
    )    
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
