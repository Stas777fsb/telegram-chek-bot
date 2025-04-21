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

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
