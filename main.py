import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
NUMVERIFY_API_KEY = "79bddad60baa9d9d54feff822627b12a"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Клавиатура
main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Проверка IP")],
    [KeyboardButton(text="Проверка номера телефона")]
], resize_keyboard=True)

# Состояния
class Form(StatesGroup):
    waiting_for_ip = State()
    waiting_for_phone = State()

@dp.message(F.text == "/start")
async def start(message: types.Message, state: FSMContext):
    await message.answer("Привет! Выбери действие:", reply_markup=main_kb)

@dp.message(F.text == "Проверка IP")
async def ip_check_start(message: types.Message, state: FSMContext):
    await message.answer("Введи IP-адрес:")
    await state.set_state(Form.waiting_for_ip)

@dp.message(Form.waiting_for_ip)
async def process_ip(message: types.Message, state: FSMContext):
    ip = message.text
    url = f"http://ip-api.com/json/{ip}?fields=66846719"
    try:
        response = requests.get(url).json()
        if response['status'] == 'success':
            result = (
                f"<b>IP:</b> {ip}\n"
                f"<b>Страна:</b> {response.get('country', '-')}\n"
                f"<b>Город:</b> {response.get('city', '-')}\n"
                f"<b>Регион:</b> {response.get('regionName', '-')}\n"
                f"<b>Провайдер:</b> {response.get('isp', '-')}\n"
                f"<b>Организация:</b> {response.get('org', '-')}\n"
                f"<b>ZIP:</b> {response.get('zip', '-')}\n"
                f"<b>Lat:</b> {response.get('lat')}, <b>Lon:</b> {response.get('lon')}\n"
                f"<b>TimeZone:</b> {response.get('timezone')}"
            )
        else:
            result = "Ошибка: IP не найден."
    except Exception as e:
        result = f"Ошибка при запросе: {e}"
    await message.answer(result)
    await state.clear()

@dp.message(F.text == "Проверка номера телефона")
async def phone_check_start(message: types.Message, state: FSMContext):
    await message.answer("Введи номер телефона с кодом страны (например, +79876543210):")
    await state.set_state(Form.waiting_for_phone)

@dp.message(Form.waiting_for_phone)
async def process_phone(message: types.Message, state: FSMContext):
    phone = message.text.replace(" ", "")
    url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone}&country_code=&format=1"
    try:
        response = requests.get(url).json()
        if response.get("valid"):
            result = (
                f"<b>Номер:</b> {phone}\n"
                f"<b>Международный формат:</b> {response.get('international_format', '-')}\n"
                f"<b>Страна:</b> {response.get('country_name', '-')}\n"
                f"<b>Оператор:</b> {response.get('carrier', '-')}\n"
                f"<b>Линия:</b> {response.get('line_type', '-')}"
            )
        else:
            result = "Номер недействителен."
    except Exception as e:
        result = f"Ошибка при проверке: {e}"
    await message.answer(result)
    await state.clear()

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
