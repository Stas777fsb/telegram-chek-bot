import asyncio
import logging
import re
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiohttp import ClientSession
from collections import defaultdict

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
IPQUALITY_API_KEY = "QUn48qWULMrgLKONUVMDJ3nG8A7
AnyCD"

FREE_LIMIT = 10
PRICE_PER_CHECK = 0.10

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
user_data = defaultdict(lambda: {"free_checks": 0, "balance": 0.0})
user_states = defaultdict(lambda: "default")

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Проверка IP")],
        [KeyboardButton(text="Проверка номера телефона")],
        [KeyboardButton(text="Проверка email")],
        [KeyboardButton(text="Пополнить баланс")]
    ],
    resize_keyboard=True
)

@dp.message(F.text == "/start")
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        f"Этот бот проверяет IP, телефоны и email на риск.\n"
        f"Ваш ID: <code>{user_id}</code>\n"
        f"Баланс: <b>${user_data[user_id]['balance']:.2f}</b>\n"
        f"Доступно бесплатных IP-проверок: <b>{FREE_LIMIT - user_data[user_id]['free_checks']}</b>",
        reply_markup=menu_keyboard
    )

@dp.message(F.text == "Проверка IP")
async def ask_ip(message: types.Message):
    user_states[message.from_user.id] = "awaiting_ip"
    await message.answer("Введите IP-адрес для проверки:")

@dp.message(F.text == "Пополнить баланс")
async def top_up_balance(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пополнить BTC")],
            [KeyboardButton(text="Пополнить LTC")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите способ пополнения:", reply_markup=keyboard)

@dp.message(F.text == "Пополнить BTC")
async def btc_topup(message: types.Message):
    await message.answer("Отправьте BTC на адрес:\n<code>19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF</code>")

@dp.message(F.text == "Пополнить LTC")
async def ltc_topup(message: types.Message):
    await message.answer("Отправьте LTC на адрес:\n<code>ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2</code>")

@dp.message(F.text == "Назад")
async def back_to_menu(message: types.Message):
    user_states[message.from_user.id] = "default"
    await message.answer("Вы вернулись в главное меню.", reply_markup=menu_keyboard)

@dp.message()
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    state = user_states[user_id]

    if state == "awaiting_ip":
        ip = message.text.strip()

        if not re.match(r"^\d{1,3}(\.\d{1,3}){3}$", ip):
            await message.answer("Неверный формат IP-адреса. Попробуйте снова.")
            return

        user_states[user_id] = "default"

# Запуск бота
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
