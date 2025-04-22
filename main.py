import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import CommandStart
from aiogram.utils import executor
import re

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
IPQUALITY_API_KEY = "QUn48qWULMrgLKONUVMDJ3nG8A7"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Проверка IP")],
        [KeyboardButton(text="Проверка email")],
        [KeyboardButton(text="Проверка телефона")]
    ],
    resize_keyboard=True
)

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Выберите действие:", reply_markup=menu)

@dp.message()
async def handle_message(message: types.Message):
    text = message.text.strip()

    if text == "Проверка IP":
        await message.answer("Введите IP-адрес:")
    elif text == "Проверка email":
        await message.answer("Введите email:")
    elif text == "Проверка телефона":
        await message.answer("Введите номер телефона в формате +1234567890:")
    elif re.match(r"^\d{1,3}(\.\d{1,3}){3}$", text):
        await check_ip(message, text)
    elif re.match(r"^\+?\d{10,15}$", text):
        await check_phone(message, text)
    elif re.match(r"[^@]+@[^@]+\.[^@]+", text):
        await check_email(message, text)
    else:
        await message.answer("Не распознанный ввод. Пожалуйста, выберите команду из меню.")

async def check_ip(message, ip):
    url = f"https://ipqualityscore.com/api/json/ip/{IPQUALITY_API_KEY}/{ip}"
    response = requests.get(url)
    data = response.json()

    risk = data.get("fraud_score", 0)
    risk_color = "🟢" if risk < 30 else "🟡" if risk < 70 else "🔴"

    result = (
        f"{risk_color} Риск: {risk}/100\n"
        f"IP: {ip}\n"
        f"Город: {data.get('city')}\n"
        f"Регион: {data.get('region')}\n"
        f"Страна: {data.get('country_name')}\n"
        f"Почтовый индекс: {data.get('zip_code')}\n"
        f"Черный список: {'Да' if data.get('is_proxy') or data.get('is_tor') else 'Нет'}"
    )
    await message.answer(result)

async def check_email(message, email):
    url = f"https://ipqualityscore.com/api/json/email/{IPQUALITY_API_KEY}/{email}"
    response = requests.get(url)
    data = response.json()

    risk = data.get("fraud_score", 0)
    valid = data.get("valid", False)
    disposable = data.get("disposable", False)

    risk_color = "🟢" if risk < 30 else "🟡" if risk < 70 else "🔴"

    result = (
        f"{risk_color} Риск: {risk}/100\n"
        f"Валидный: {'Да' if valid else 'Нет'}\n"
        f"Disposable: {'Да' if disposable else 'Нет'}"
    )
    await message.answer(result)

async def check_phone(message, phone):
    url = f"https://ipqualityscore.com/api/json/phone/{IPQUALITY_API_KEY}/{phone}"
    response = requests.get(url)
    data = response.json()

    risk = data.get("fraud_score", 0)
    active = data.get("active_status", "unknown")
    carrier = data.get("carrier", "неизвестно")

    risk_color = "🟢" if risk < 30 else "🟡" if risk < 70 else "🔴"

    result = (
        f"{risk_color} Риск: {risk}/100\n"
        f"Статус: {active}\n"
        f"Оператор: {carrier}\n"
        f"Тип: {data.get('line_type')}"
    )
    await message.answer(result)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
