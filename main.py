import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
ABSTRACT_API_KEY = "76599f16ac4f4a359808485a87a8f3bd"
NUMVERIFY_API_KEY = "79bddad60baa9d9d54feff822627b12a"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Стейт-машина для выбора проверки
class Form(StatesGroup):
    waiting_for_ip = State()
    waiting_for_email = State()
    waiting_for_phone = State()

# Главное меню
def main_menu():
    keyboard = [
        [InlineKeyboardButton(text="Проверка IP", callback_data="check_ip")],
        [InlineKeyboardButton(text="Проверка email", callback_data="check_email")],
        [InlineKeyboardButton(text="Проверка телефона", callback_data="check_phone")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

@dp.message(F.text, F.text.lower().in_(["/start", "старт", "начать"]))
async def start_handler(message: Message):
    await message.answer("Выберите тип проверки:", reply_markup=main_menu())
@dp.callback_query(F.data == "check_ip")
async def process_ip_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите IP-адрес для проверки:")
    await state.set_state(Form.waiting_for_ip)
    await callback.answer()

@dp.message(Form.waiting_for_ip)
async def handle_ip_input(message: Message, state: FSMContext):
    ip = message.text.strip()
    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address={ip}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
    
    risk_score = int(data.get("security", {}).get("threat_score", 0))
    color = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"
    info = f"""
<b>Проверка IP:</b> {ip}
<b>Страна:</b> {data.get("country")}
<b>Город:</b> {data.get("city")}
<b>ZIP:</b> {data.get("postal_code")}
<b>Провайдер:</b> {data.get("connection", {}).get("isp_name")}
<b>VPN/Proxy:</b> {'Да' if data.get("security", {}).get("is_vpn") or data.get("security", {}).get("is_proxy") else 'Нет'}
<b>Оценка риска:</b> {risk_score}/100 {color}
"""
    await message.answer(info.strip(), parse_mode=ParseMode.HTML)
    await state.clear()
@dp.callback_query(F.data == "check_email")
async def process_email_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите email для проверки:")
    await state.set_state(Form.waiting_for_email)
    await callback.answer()
 @dp.message(Form.waiting_for_email)
async def handle_email_input(message: Message, state: FSMContext):
    email = message.text.strip()
    url = f"https://emailvalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&email={email}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    risk_score = 0
    if not data.get("is_valid_format", {}).get("value"):
        risk_score += 40
    if data.get("is_disposable", {}).get("value"):
        risk_score += 30
    if not data.get("is_smtp_valid", {}).get("value"):
        risk_score += 30

    color = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"
    
    info = f"""
<b>Проверка Email:</b> {email}
<b>Формат:</b> {'Корректный' if data.get("is_valid_format", {}).get("value") else 'Некорректный'}
<b>Существует:</b> {'Да' if data.get("is_smtp_valid", {}).get("value") else 'Нет'}
<b>Провайдер:</b> {data.get("domain")}
<b>Временный:</b> {'Да' if data.get("is_disposable", {}).get("value") else 'Нет'}
<b>Оценка риска:</b> {risk_score}/100 {color}
"""
    await message.answer(info.strip(), parse_mode=ParseMode.HTML)
    await state.clear()
@dp.callback_query(F.data == "check_phone")
async def process_phone_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите номер телефона для проверки (в международном формате, например: +14158586273):")
    await state.set_state(Form.waiting_for_phone)
    await callback.answer()
 @dp.message(Form.waiting_for_phone)
async def handle_phone_input(message: Message, state: FSMContext):
    phone = message.text.strip().replace(" ", "")
    url = f"https://phonevalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&phone={phone}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    risk_score = 0
    if not data.get("valid"):
        risk_score += 50
    if not data.get("line_type") or data.get("line_type") == "unknown":
        risk_score += 25
    if not data.get("carrier"):
        risk_score += 25

    color = "🟢" if risk_score < 30 else "🟡" if risk_score < 70 else "🔴"

    info = f"""
<b>Проверка телефона:</b> {phone}
<b>Страна:</b> {data.get("country", {}).get("name", "Неизвестно")}
<b>Оператор:</b> {data.get("carrier", "Неизвестно")}
<b>Тип линии:</b> {data.get("line_type", "Неизвестно")}
<b>Формат:</b> {'Корректный' if data.get("valid") else 'Некорректный'}
<b>Оценка риска:</b> {risk_score}/100 {color}
"""
    await message.answer(info.strip(), parse_mode=ParseMode.HTML)
    await state.clear()   
