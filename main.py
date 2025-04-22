import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram import Router
import aiohttp
from datetime import datetime, timedelta

API_KEY = "76599f16ac4f4a359808485a87a8f3bd"
BTC_WALLET = "19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF"
LTC_WALLET = "ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token="7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU", parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

user_data = {}

class CheckState(StatesGroup):
    ip = State()
    email = State()
    phone = State()

main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Проверка IP"), KeyboardButton(text="Проверка email")],
    [KeyboardButton(text="Проверка номера телефона")],
    [KeyboardButton(text="Пополнить баланс")]
], resize_keyboard=True)

def get_color_for_risk(score):
    if score < 30:
        return "🟢"
    elif score < 70:
        return "🟡"
    else:
        return "🔴"

@router.message(CommandStart())
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {
            "balance": 0.0,
            "free_ip_checks": 10,
            "last_reset": datetime.utcnow().date()
        }
    await message.answer(f"Добро пожаловать, {hbold(message.from_user.first_name)}!\n\n"
                         f"Ваш ID: <code>{user_id}</code>\n"
                         f"Баланс: <b>{user_data[user_id]['balance']:.2f}$</b>\n"
                         f"Доступно бесплатных IP-проверок: {user_data[user_id]['free_ip_checks']}",
                         reply_markup=main_kb)

@router.message(F.text == "Проверка IP")
async def ask_ip(message: types.Message, state: FSMContext):
    await state.set_state(CheckState.ip)
    await message.answer("Введите IP-адрес для проверки:")

@router.message(CheckState.ip)
async def check_ip(message: types.Message, state: FSMContext):
    ip = message.text
    user_id = message.from_user.id
    today = datetime.utcnow().date()
    user = user_data[user_id]

    if user["last_reset"] != today:
        user["last_reset"] = today
        user["free_ip_checks"] = 10

    if user["free_ip_checks"] <= 0 and user["balance"] < 0.10:
        await message.answer("У вас закончились бесплатные проверки и недостаточно средств на балансе.")
        return

    if user["free_ip_checks"] > 0:
        user["free_ip_checks"] -= 1
    else:
        user["balance"] -= 0.10

    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={API_KEY}&ip_address={ip}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    risk_score = 80 if data.get("is_vpn", False) else 20
    color = get_color_for_risk(risk_score)

    text = (
        f"{color} <b>IP:</b> {ip}\n"
        f"<b>Страна:</b> {data.get('country')}\n"
        f"<b>Регион:</b> {data.get('region')}\n"
        f"<b>Город:</b> {data.get('city')}\n"
        f"<b>Почтовый индекс:</b> {data.get('postal_code')}\n"
        f"<b>Провайдер:</b> {data.get('connection', {}).get('isp_name')}\n"
        f"<b>VPN/Proxy:</b> {'Да' if data.get('is_vpn') else 'Нет'}\n"
        f"<b>Оценка риска:</b> {risk_score}/100"
    )
    await state.clear()
    await message.answer(text)

@router.message(F.text == "Проверка email")
async def ask_email(message: types.Message, state: FSMContext):
    await state.set_state(CheckState.email)
    await message.answer("Введите email для проверки:")

@router.message(CheckState.email)
async def check_email(message: types.Message, state: FSMContext):
    email = message.text
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={API_KEY}&email={email}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    risk_score = 80 if data.get("is_disposable_email") else 20
    color = get_color_for_risk(risk_score)

    text = (
        f"{color} <b>Email:</b> {email}\n"
        f"<b>Валиден:</b> {'Да' if data.get('is_valid_format', {}).get('value') else 'Нет'}\n"
        f"<b>Временный:</b> {'Да' if data.get('is_disposable_email') else 'Нет'}\n"
        f"<b>Домен:</b> {data.get('domain')}\n"
        f"<b>Оценка риска:</b> {risk_score}/100"
    )
    await state.clear()
    await message.answer(text)

@router.message(F.text == "Проверка номера телефона")
async def ask_phone(message: types.Message, state: FSMContext):
    await state.set_state(CheckState.phone)
    await message.answer("Введите номер телефона (в формате +71234567890):")

@router.message(CheckState.phone)
async def check_phone(message: types.Message, state: FSMContext):
    phone = message.text
    url = f"https://phonevalidation.abstractapi.com/v1/?api_key={API_KEY}&phone={phone}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    risk_score = 20 if data.get("valid") else 90
    color = get_color_for_risk(risk_score)

    text = (
        f"{color} <b>Номер:</b> {phone}\n"
        f"<b>Валиден:</b> {'Да' if data.get('valid') else 'Нет'}\n"
        f"<b>Страна:</b> {data.get('country', {}).get('name')}\n"
        f"<b>Оператор:</b> {data.get('carrier')}\n"
        f"<b>Формат:</b> {data.get('format', {}).get('international')}\n"
        f"<b>Оценка риска:</b> {risk_score}/100"
    )
    await state.clear()
    await message.answer(text)

@router.message(F.text == "Пополнить баланс")
async def top_up(message: types.Message):
    await message.answer(
        "<b>Выберите способ пополнения:</b>\n\n"
        f"<b>BTC:</b>\n<code>{BTC_WALLET}</code>\n\n"
        f"<b>LTC:</b>\n<code>{LTC_WALLET}</code>"
    )

if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
