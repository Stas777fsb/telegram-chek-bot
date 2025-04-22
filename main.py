import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import hbold
from aiogram import F

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
IPQUALITY_API_KEY = "QUn48qWULMrgLKONUVMDJ3nG8A7"
BTC_ADDRESS = "19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF"
LTC_ADDRESS = "ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"{hbold('Добро пожаловать!')}\n\n"
        "Выберите действие:",
        reply_markup=types.ReplyKeyboardMarkup(
            keyboard=[
                [types.KeyboardButton(text="Проверка IP")],
                [types.KeyboardButton(text="Проверка email")],
                [types.KeyboardButton(text="Проверка номера телефона")],
                [types.KeyboardButton(text="Пополнить баланс")]
            ],
            resize_keyboard=True
        )
    )

@dp.message(F.text.lower() == "проверка ip")
async def check_ip(message: Message):
    await message.answer("Введите IP-адрес:")
    dp.message.register(handle_ip)

async def handle_ip(message: Message):
    ip = message.text.strip()
    response = requests.get(f"https://ipqualityscore.com/api/json/ip/{IPQUALITY_API_KEY}/{ip}").json()

    risk_score = int(response.get("fraud_score", 0))
    color = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"
    blacklist_info = "Да" if response.get("proxy") or response.get("tor") or response.get("vpn") else "Нет"

    await message.answer(
        f"<b>Результат для IP:</b> {ip}\n"
        f"Страна: {response.get('country_code')}\n"
        f"Город: {response.get('city')}\n"
        f"ZIP: {response.get('zipcode')}\n"
        f"Провайдер: {response.get('ISP')}\n"
        f"Риск: {color} {risk_score}/100\n"
        f"В черных списках: {blacklist_info}"
    )

@dp.message(F.text.lower() == "проверка email")
async def check_email_prompt(message: Message):
    await message.answer("Введите email:")
    dp.message.register(handle_email)

async def handle_email(message: Message):
    email = message.text.strip()
    response = requests.get(f"https://ipqualityscore.com/api/json/email/{IPQUALITY_API_KEY}/{email}").json()
    risk_score = int(response.get("fraud_score", 0))
    deliverable = "Да" if response.get("deliverability") == "high" else "Нет"
    color = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"

    await message.answer(
        f"<b>Результат для email:</b> {email}\n"
        f"Риск: {color} {risk_score}/100\n"
        f"Доставляемость: {deliverable}\n"
        f"Провайдер: {response.get('domain')}"
    )

@dp.message(F.text.lower() == "проверка номера телефона")
async def check_phone_prompt(message: Message):
    await message.answer("Введите номер телефона в международном формате (например, +79991234567):")
    dp.message.register(handle_phone)

async def handle_phone(message: Message):
    phone = message.text.strip()
    response = requests.get(f"https://ipqualityscore.com/api/json/phone/{IPQUALITY_API_KEY}/{phone}").json()
    risk_score = int(response.get("fraud_score", 0))
    valid = "Да" if response.get("valid") else "Нет"
    carrier = response.get("carrier") or "Неизвестен"
    region = response.get("region") or "Неизвестно"
    color = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"

    await message.answer(
        f"<b>Результат для телефона:</b> {phone}\n"
        f"Риск: {color} {risk_score}/100\n"
        f"Действителен: {valid}\n"
        f"Оператор: {carrier}\n"
        f"Регион: {region}"
    )

@dp.message(F.text.lower() == "пополнить баланс")
async def top_up_balance(message: Message):
    await message.answer(
        f"<b>Пополнение баланса:</b>\n\n"
        f"BTC: <code>{BTC_ADDRESS}</code>\n"
        f"LTC: <code>{LTC_ADDRESS}</code>\n\n"
        f"После оплаты напишите в поддержку с указанием суммы и ID: <code>{message.from_user.id}</code>"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
