import os
import asyncio
import random
import aiohttp
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from collections import defaultdict

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Баланс и лимиты
user_balances = defaultdict(lambda: 0.00)
user_check_limits = {}

# BTC / LTC адреса
BTC_ADDRESS = "19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF"
LTC_ADDRESS = "ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2"

# Главное меню
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="Проверка IP")],
        [KeyboardButton(text="Проверка номера телефона")],
        [KeyboardButton(text="Проверка email")],
        [KeyboardButton(text="Пополнить баланс")],
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# Команда /start
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

# Запрос IP-адреса
@dp.message(F.text == "Проверка IP")
async def ask_for_ip(message: Message):
    await message.answer("Отправьте IP-адрес для проверки:")

# Проверка IP
@dp.message(F.text.regexp(r"^\d{1,3}(\.\d{1,3}){3}$"))
async def check_ip(message: Message):
    user_id = message.from_user.id
    ip = message.text.strip()
    today = datetime.utcnow().date()

    if user_id not in user_check_limits or user_check_limits[user_id]["date"] != today:
        user_check_limits[user_id] = {"date": today, "count": 0}

    if user_check_limits[user_id]["count"] >= 10:
        if user_balances[user_id] >= 0.10:
            user_balances[user_id] -= 0.10
        else:
            await message.answer("Вы израсходовали 10 бесплатных проверок сегодня.\nНедостаточно средств для платной проверки ($0.10).")
            return
    else:
        user_check_limits[user_id]["count"] += 1

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,query,isp,org,as,lat,lon") as resp:
                data = await resp.json()
                if data.get("status") == "fail":
                    await message.answer(f"Ошибка: {data.get('message')}")
                    return

        risk_score = random.randint(0, 100)

        text = (
            f"<b>IP:</b> <code>{data.get('query')}</code>\n"
            f"<b>Страна:</b> {data.get('country')}\n"
            f"<b>Регион:</b> {data.get('regionName')}\n"
            f"<b>Город:</b> {data.get('city')}\n"
            f"<b>Провайдер:</b> {data.get('isp')}\n"
            f"<b>Организация:</b> {data.get('org')}\n"
            f"<b>AS:</b> {data.get('as')}\n"
            f"<b>Координаты:</b> {data.get('lat')}, {data.get('lon')}\n"
            f"<b>Риск:</b> {risk_score}%"
        )

        await message.answer(text, parse_mode="HTML")
    except Exception as e:
        await message.answer(f"Ошибка при проверке IP: {str(e)}")

# Заглушки
@dp.message(F.text == "Проверка номера телефона")
async def handle_phone(message: Message):
    await message.answer("Функция проверки номера телефона будет доступна позже.")

@dp.message(F.text == "Проверка email")
async def handle_email(message: Message):
    await message.answer("Функция проверки email будет доступна позже.")

@dp.message(F.text == "Пополнить баланс")
async def handle_topup(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Пополнить BTC")],
            [KeyboardButton(text="Пополнить LTC")],
            [KeyboardButton(text="Назад в меню")]
        ],
        resize_keyboard=True
    )
    awa
it message.answer("Выберите способ пополнения:", reply_markup=keyboard)

@dp.message(F.text == "Пополнить BTC")
async def btc_topup(message: Message):
    await message.answer(f"Переведите BTC на адрес:\n<code>{BTC_ADDRESS}</code>", parse_mode="HTML")

@dp.message(F.text == "Пополнить LTC")
async def ltc_topup(message: Message):
    await message.answer(f"Переведите LTC на адрес:\n<code>{LTC_ADDRESS}</code>", parse_mode="HTML")

@dp.message(F.text == "Назад в меню")
async def back_to_menu(message: Message):
    user_id = message.from_user.id
    balance = user_balances[user_id]
    await message.answer(
        f"<b>Ваш ID:</b> <code>{user_id}</code>\n"
        f"<b>Баланс:</b> ${balance:.2f}\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

# Запуск
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
