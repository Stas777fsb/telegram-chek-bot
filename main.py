import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiohttp import ClientSession
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.markdown import hbold

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Укажи токен бота прямо здесь (НЕ РЕКОМЕНДУЕТСЯ для продакшна)
API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
NUMVERIFY_API_KEY = "79bddad60baa9d9d54feff822627b12a"
ABSTRACT_API_KEY = "76599f16ac4f4a359808485a87a8f3bd"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())


@dp.message(commands=["start"])
async def start_handler(message: Message):
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}!\nВыбери, что хочешь проверить:\n\n"
                         "/check_ip — Проверить IP\n"
                         "/check_phone — Проверить номер телефона\n"
                         "/check_email — Проверить email")


@dp.message(commands=["check_ip"])
async def check_ip(message: Message):
    await message.answer("Отправь IP-адрес для проверки.")


@dp.message(commands=["check_phone"])
async def check_phone(message: Message):
    await message.answer("Отправь номер телефона в формате +71234567890.")


@dp.message(commands=["check_email"])
async def check_email(message: Message):
    await message.answer("Отправь email для проверки.")


@dp.message()
async def handle_input(message: Message):
    text = message.text.strip()

    if text.count(".") == 3:  # вероятно IP
        await check_ip_info(message, text)
    elif "@" in text:  # email
        await check_email_info(message, text)
    elif text.startswith("+") and text[1:].isdigit():
        await check_phone_info(message, text)
    else:
        await message.answer("Не могу определить формат. Попробуй ещё раз.")


async def check_ip_info(message: Message, ip: str):
    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address={ip}"
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    risk_score = data.get("security", {}).get("threat_score", 0)
    risk_color = "🟢" if risk_score < 40 else "🟡" if risk_score < 70 else "🔴"

    msg = (f"{risk_color} <b>IP:</b> {ip}\n"
           f"<b>Страна:</b> {data.get('country')}\n"
           f"<b>Регион:</b> {data.get('region')}\n"
           f"<b>Город:</b> {data.get('city')}\n"
           f"<b>Почтовый индекс:</b> {data.get('postal_code')}\n"
           f"<b>Провайдер:</b> {data.get('connection', {}).get('isp_name')}\n"
           f"<b>VPN/Proxy:</b> {'Да' if data.get('security', {}).get('is_vpn') else 'Нет'}\n"
           f"<b>Оценка риска:</b> {risk_score}/100")
    await message.answer(msg)


async def check_phone_info(message: Message, phone: str):
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone}&format=1"
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    valid = data.get("valid")
    risk = 90 if not valid else 10
    risk_color = "🟢" if risk < 40 else "🟡" if risk < 70 else "🔴"

    msg = (f"{risk_color} <b>Номер:</b> {phone}\n"
           f"<b>Валиден:</b> {'Да' if valid else 'Нет'}\n"
           f"<b>Страна:</b> {data.get('country_name')}\n"
           f"<b>Оператор:</b> {data.get('carrier')}\n"
           f"<b>Формат:</b> {data.get('international_format')}\n"
           f"<b>Оценка риска:</b> {risk}/100")
    await message.answer(msg)


async def check_email_info(message: Message, email: str):
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&email={email}"
    async with ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    risk_score = 80 if not data.get("deliverability") == "DELIVERABLE" else 10
    risk_color = "🟢" if risk_score < 40 else "🟡" if risk_score < 70 else "🔴"

    msg = (f"{risk_color} <b>Email:</b> {email}\n"
           f"<b>Валиден:</b> {'Да' if data.get('is_valid_format', {}).get('value') else 'Нет'}\n"
           f"<b>Домен:</b> {data.get('domain')}\n"
           f"<b>Оценка риска:</b> {risk_score}/100")
    await message.answer(msg)


if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
