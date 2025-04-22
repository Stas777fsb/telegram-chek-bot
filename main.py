import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import aiohttp
import asyncio
import os

API_TOKEN = os.getenv("7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU") NUMVERIFY_API_KEY = "79bddad60baa9d9d54feff822627b12a" ABSTRACT_API_KEY = "76599f16ac4f4a359808485a87a8f3bd"

logging.basicConfig(level=logging.INFO) logger = logging.getLogger(name)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML) dp = Dispatcher(storage=MemoryStorage())

class CheckState(StatesGroup): phone = State()

@dp.message(lambda message: message.text == "Проверка номера телефона") async def phone_check_command(message: Message, state: FSMContext): await message.answer("Введите номер телефона (в формате +71234567890):") await state.set_state(CheckState.phone)

@dp.message(CheckState.phone) async def handle_phone(message: Message, state: FSMContext): phone = message.text.strip()

result_text = f"🔍 <b>Номер:</b> {phone}\n"

async with aiohttp.ClientSession() as session:
    # Проверка через Numverify
    async with session.get(
        f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone}&format=1"
    ) as resp:
        data = await resp.json()
        valid = data.get("valid")
        country = data.get("country_name")
        operator = data.get("carrier")

    result_text += f"<b>Валиден:</b> {'Да' if valid else 'Нет'}\n"
    result_text += f"<b>Страна:</b> {country if country else 'Неизвестна'}\n"
    result_text += f"<b>Оператор:</b> {operator if operator else 'Неизвестен'}\n"

    # Оценка риска через Abstract
    async with session.get(
        f"https://phonevalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&phone={phone}"
    ) as abstract_resp:
        abstract_data = await abstract_resp.json()
        risk = abstract_data.get("risk_score", 0)

    # Предположительно: наличие в соцсетях по стране и оператору (заглушка)
    social_flag = "Да" if valid and country and operator else "Нет"
   
    result_text += f"<b>Наличие в соцсетях:</b> {social_flag}\n"
    result_text += f"<b>Оценка риска:</b> {risk}/100"

await message.answer(result_text)
await state.clear()

@dp.message() async def main_menu(message: Message): builder = ReplyKeyboardBuilder() builder.button(text="Проверка номера телефона") builder.adjust(1)

await message.answer("Выберите действие:", reply_markup=builder.as_markup(resize_keyboard=True))

if name == "main": asyncio.run(dp.start_polling(bot))
