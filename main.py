import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroupState
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder

API_KEY = "76599f16ac4f4a359808485a87a8f3bd"

bot = Bot(token="...", parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class CheckState(StatesGroup): ip = State() email = State() phone = State()

main_keyboard = ReplyKeyboardMarkup(keyboard=[ [KeyboardButton(text="Проверка IP")], [KeyboardButton(text="Проверка email")], [KeyboardButton(text="Проверка номера телефона")] ], resize_keyboard=True)

@dp.message(F.text == "/start") async def start(message: Message): await message.answer("Выберите действие:", reply_markup=main_keyboard)

@dp.message(F.text == "Проверка IP") async def ask_ip(message: Message, state: FSMContext): await message.answer("Введи IP-адрес:") await state.set_state(CheckState.ip)

@dp.message(CheckState.ip) async def check_ip(message: Message, state: FSMContext): ip = message.text url = f"https://ipqualityscore.com/api/json/ip/{API_KEY}/{ip}" response = requests.get(url).json()

risk_score = response.get("fraud_score")
vpn = response.get("vpn")
proxy = response.get("proxy")
tor = response.get("tor")
open_ports = response.get("open_ports")
blacklist = response.get("recent_abuse")

text = f"<b>IP: {ip}</b>\n"
text += f"Риск: <b>{risk_score}/100</b>\n"
text += f"VPN: {'Да' if vpn else 'Нет'}\n"
text += f"Proxy: {'Да' if proxy else 'Нет'}\n"
text += f"Tor: {'Да' if tor else 'Нет'}\n"
text += f"Открытые порты: {', '.join(map(str, open_ports)) if open_ports else 'Не обнаружены'}\n"
text += f"В черных списках: {'Да' if blacklist else 'Нет'}"

await message.answer(text)
await state.clear()

@dp.message(F.text == "Проверка email") async def ask_email(message: Message, state: FSMContext): await message.answer("Введи email:") await state.set_state(CheckState.email)

@dp.message(CheckState.email) async def check_email(message: Message, state: FSMContext): email = message.text url = f"https://emailvalidation.abstractapi.com/v1/?api_key={API_KEY}&email={email}" response = requests.get(url).json()

deliverable = response.get("deliverability")
is_valid = response.get("is_valid_format", {}).get("value")
is_disposable = response.get("is_disposable_email", {}).get("value")
is_free = response.get("is_free_email", {}).get("value")
spam = response.get("is_spam", {}).get("value")

text = f"<b>Email: {email}</b>\n"
text += f"Доставляемость: {deliverable}\n"
text += f"Формат: {'ОК' if is_valid else 'Ошибка'}\n"
text += f"Временная: {'Да' if is_disposable else 'Нет'}\n"
text += f"Бесплатная: {'Да' if is_free else 'Нет'}\n"
text += f"Спам: {'Да' if spam else 'Нет'}"

await message.answer(text)
await state.clear()

@dp.message(F.text == "Проверка номера телефона") async def ask_phone(message: Message, state: FSMContext): await message.answer("Введи номер телефона с кодом страны (например, +79876543210):") await state.set_state(CheckState.phone)

@dp.message(CheckState.phone) async def check_phone(message: Message, state: FSMContext): phone = message.text url = f"https://phonevalidation.abstractapi.com/v1/?api_key={API_KEY}&phone={phone}" response = requests.get(url).json()

country = response.get("country")
location = response.get("location")
carrier = response.get("carrier")
line_type = response.get("line_type")
valid = response.get("valid")

text = f"<b>Номер: {phone}</b>\n"
text += f"Страна: {country}\n"
text += f"Регион: {location}\n"
text += f"Оператор: {carrier}\n"
text += f"Тип линии: {line_type}\n"
text += f"Действительный: {'Да' if valid else 'Нет'}"

await message.answer(text)
await state.clear()

async def main(): logging.basicConfig(level=logging.INFO) await dp.start_polling(bot)

if name == "main": asyncio.run(main())
