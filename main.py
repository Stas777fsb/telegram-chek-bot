import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage

# КЛЮЧИ И ТОКЕНЫ (замени на свои при необходимости)
API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
IPQS_API_KEY = "QUn48qWULMrgLKONUVMDJ3nG8A7AnyCD"
NUMVERIFY_API_KEY = "QUn48qWULMrgLKONUVMDJ3nG8A7AnyCD"

FREE_CHECKS = 10
btc_address = "19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF"
ltc_address = "ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2"

users_data = {}

class MenuStates(StatesGroup):
    waiting_for_ip = State()
    waiting_for_email = State()
    waiting_for_phone = State()

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Проверка IP")],
    [KeyboardButton(text="Проверка email")],
    [KeyboardButton(text="Проверка номера телефона")],
    [KeyboardButton(text="Пополнить баланс")]
], resize_keyboard=True)

def get_risk_color(risk_score: int) -> str:
    if risk_score < 20:
        return "🟢"
    elif risk_score < 60:
        return "🟡"
    else:
        return "🔴"

@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    user_id = str(message.from_user.id)
    if user_id not in users_data:
        users_data[user_id] = {"balance": 0, "free_checks": FREE_CHECKS}
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n"
        f"Твой ID: <code>{user_id}</code>\n"
        f"Баланс: ${users_data[user_id]['balance']:.2f}\n"
        f"Бесплатных проверок сегодня: {users_data[user_id]['free_checks']}",
        reply_markup=main_menu
    )

@dp.message(F.text == "Проверка IP")
async def ask_ip(message: Message, state: FSMContext):
    await state.set_state(MenuStates.waiting_for_ip)
    await message.answer("Отправь IP-адрес для проверки:")

@dp.message(MenuStates.waiting_for_ip)
async def check_ip(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    ip = message.text.strip()

    response = requests.get(f"https://ipqualityscore.com/api/json/ip/{IPQS_API_KEY}/{ip}").json()
    risk_score = response.get("fraud_score", 0)
    country = response.get("country_code", "N/A")
    city = response.get("city", "N/A")
    zip_code = response.get("zip_code", "N/A")
    blacklisted = response.get("blacklist", False)

    color = get_risk_color(risk_score)
    text = (
        f"<b>Результат для IP {ip}</b>\n"
        f"Риск: {risk_score} {color}\n"
        f"Страна: {country}, Город: {city}\n"
        f"ZIP: {zip_code}\n"
        f"Черный список: {'Да' if blacklisted else 'Нет'}"
    )

    if users_data[user_id]["free_checks"] > 0:
        users_data[user_id]["free_checks"] -= 1
    elif users_data[user_id]["balance"] >= 0.1:
        users_data[user_id]["balance"] -= 0.1
    else:
        await message.answer("Недостаточно баланса. Пополни баланс.")
        await state.clear()
        return

    await message.answer(text)
    await state.clear()

@dp.message(F.text == "Проверка email")
async def ask_email(message: Message, state: FSMContext):
    await state.set_state(MenuStates.waiting_for_email)
    await message.answer("Отправь email для проверки:")

@dp.message(MenuStates.waiting_for_email)
async def check_email(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    email = message.text.strip()

    response = requests.get(f"https://ipqualityscore.com/api/json/email/{IPQS_API_KEY}/{email}").json()
    valid = response.get("valid", False)
    disposable = response.get("disposable", False)
    recent_abuse = response.get("recent_abuse", False)
    risk_score = response.get("fraud_score", 0)

    color = get_risk_color(risk_score)
    text = (
        f"<b>Результат для {email}</b>\n"
        f"Риск: {risk_score} {color}\n"
        f"Валидный: {'Да' if valid else 'Нет'}\n"
        f"Disposable: {'Да' if disposable else 'Нет'}\n"
        f"Abuse: {'Да' if recent_abuse else 'Нет'}"
    )

    if users_data[user_id]["free_checks"] > 0:
        users_data[user_id]["free_checks"] -= 1
    elif users_data[user_id]["balance"] >= 0.1:
        users_data[user_id]["balance"] -= 0.1
    else:
        await message.answer("Недостаточно баланса. Пополни баланс.")
        await state.clear()
        return

    await message.answer(text)
    await state.clear()

@dp.message(F.text == "Проверка номера телефона")
async def ask_phone(message: Message, state: FSMContext):
    await state.set_state(MenuStates.waiting_for_phone)
    await message.answer("Отправь номер телефона (в формате +123456789):")

@dp.message(MenuStates.waiting_for_phone)
async def check_phone(message: Message, state: FSMContext):
    user_id = str(message.from_user.id)
    phone = message.text.strip()

    response = requests.get(f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={phone}&format=1").json()

    if "valid" not in response:
        await message.answer("Ошибка проверки номера. Проверь формат.")
        await state.clear()
        return

    risk_score = 0 if response["valid"] else 80
    color = get_risk_color(risk_score)

    text = (
        f"<b>Результат для {phone}</b>\n"
        f"Риск: {risk_score} {color}\n"
        f"Валидный: {'Да' if response['valid'] else 'Нет'}\n"
        f"Страна: {response.get('country_name', 'N/A')}\n"
        f"Локальный формат: {response.get('local_format', 'N/A')}\n"
        f"Оператор: {response.get('carrier', 'N/A')}"
    )

    if users_data[user_id]["free_checks"] > 0:
        users_data[user_id]["free_checks"] -= 1
    elif users_data[user_id]["balance"] >= 0.1:
        users_data[user_id]["balance"] -= 0.1
    else:
        await message.answer("Недостаточно баланса. Пополни баланс.")
        await state.clear()
        return

    await message.answer(text)
    await state.clear()

@dp.message(F.text == "Пополнить баланс")
async def top_up(message: Message):
    await message.answer(
        f"Пополнение BTC: <code>{btc_address}</code>\n"
        f"Пополнение LTC: <code>{ltc_address}</code>\n\n"
        f"После оплаты напиши /start для обновления баланса вручную."
    )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
