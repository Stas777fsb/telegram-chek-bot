import asyncio
from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
from datetime import datetime, timedelta

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
ABSTRACT_API_KEY = "76599f16ac4f4a359808485a87a8f3bd"
NUMVERIFY_API_KEY = "79bddad60baa9d9d54feff822627b12a"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
router = Router()
dp.include_router(router)

users_data = {}

BTC_ADDRESS = "19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF"
LTC_ADDRESS = "ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2"

FREE_IP_CHECKS_PER_DAY = 10
CHECK_COST = 0.10

# === КНОПКИ ===
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="Проверка IP", callback_data="check_ip")
    kb.button(text="Проверка email", callback_data="check_email")
    kb.button(text="Проверка телефона", callback_data="check_phone")
    kb.button(text="Пополнить баланс", callback_data="top_up")
    return kb.as_markup()

# === ХЕЛПЕР ===
def get_user(uid):
    if uid not in users_data:
        users_data[uid] = {
            "balance": 0.0,
            "ip_checks": 0,
            "last_reset": datetime.now()
        }
    if datetime.now() - users_data[uid]["last_reset"] > timedelta(days=1):
        users_data[uid]["ip_checks"] = 0
        users_data[uid]["last_reset"] = datetime.now()
    return users_data[uid]

# === СТАРТ ===
@router.message(F.text == "/start")
async def start_handler(message: Message):
    uid = message.from_user.id
    get_user(uid)
    await message.answer(
        f"👋 Привет, {message.from_user.full_name}!\n\nID: <code>{uid}</code>\nБаланс: <b>{users_data[uid]['balance']:.2f}$</b>",
        reply_markup=main_menu()
    )

# === IP CHECK ===
@router.callback_query(F.data == "check_ip")
async def ask_ip(callback: types.CallbackQuery):
    await callback.message.answer("Введите IP-адрес для проверки:")
    await dp.fsm.set("waiting_for_ip")

@router.message(F.state == "waiting_for_ip")
async def process_ip(message: Message):
    uid = message.from_user.id
    user = get_user(uid)
    ip = message.text.strip()

    if user["ip_checks"] < FREE_IP_CHECKS_PER_DAY:
        user["ip_checks"] += 1
    elif user["balance"] >= CHECK_COST:
        user["balance"] -= CHECK_COST
    else:
        await message.answer("❌ Превышен лимит бесплатных проверок и недостаточно средств.")
        return

    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address={ip}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    result = f"<b>IP:</b> {data.get('ip_address')}\n<b>Страна:</b> {data.get('country')}\n<b>Регион:</b> {data.get('region')}\n<b>Город:</b> {data.get('city')}\n<b>Провайдер:</b> {data.get('connection', {}).get('isp')}\n<b>VPN/Proxy:</b> {data.get('security', {}).get('is_vpn', False)}"
    await message.answer(result, reply_markup=main_menu())
    await dp.fsm.reset()

# === EMAIL CHECK ===
@router.callback_query(F.data == "check_email")
async def ask_email(callback: types.CallbackQuery):
    await callback.message.answer("Введите email для проверки:")
    await dp.fsm.set("waiting_for_email")

@router.message(F.state == "waiting_for_email")
async def process_email(message: Message):
    email = message.text.strip()
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&email={email}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    result = f"<b>Email:</b> {data.get('email')}\n<b>Реален:</b> {data.get('is_valid_format', {}).get('value')}\n<b>Существует:</b> {data.get('is_smtp_valid', {}).get('value')}\n<b>Спам:</b> {data.get('is_suspect', {}).get('value')}"
    await message.answer(result, reply_markup=main_menu())
    await dp.fsm.reset()

# === PHONE CHECK ===
@router.callback_query(F.data == "check_phone")
async def ask_phone(callback: types.CallbackQuery):
    await callback.message.answer("Введите номер телефона (в международном формате):")
    await dp.fsm.set("waiting_for_phone")

@router.message(F.state == "waiting_for_phone")
async def process_phone(message: Message):
    phone = message.text.strip()
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone}&format=1"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    result = f"<b>Номер:</b> {data.get('international_format')}\n<b>Страна:</b> {data.get('country_name')}\n<b>Оператор:</b> {data.get('carrier')}\n<b>Тип:</b> {data.get('line_type')}"
    await message.answer(result, reply_markup=main_menu())
    await dp.fsm.reset()

# === TOP UP ===
@router.callback_query(F.data == "top_up")
async def top_up(callback: types.CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="Пополнить BTC", callback_data="btc")
    kb.button(text="Пополнить LTC", callback_data="ltc")
    await callback.message.answer("Выберите способ пополнения:", reply_markup=kb.as_markup())

@router.callback_query(F.data == "btc")
async def btc_address(callback: types.CallbackQuery):
    await callback.message.answer(f"💰 BTC-адрес: <code>{BTC_ADDRESS}</code>")

@router.callback_query(F.data == "ltc")
async def ltc_address(callback: types.CallbackQuery):
    await callback.message.answer(f"💰 LTC-адрес: <code>{LTC_ADDRESS}</code>")

# === ЗАПУСК ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
