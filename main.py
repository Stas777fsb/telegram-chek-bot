import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

# Хранилище пользователей
USERS = {}
MAX_FREE_CHECKS = 10
BTC_ADDRESS = "19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF"
LTC_ADDRESS = "ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2"

class Form(StatesGroup):
    waiting_for_ip = State()
    waiting_for_email = State()
    waiting_for_phone = State()

def main_menu():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Проверка IP", callback_data="check_ip")
    keyboard.button(text="Проверка Email", callback_data="check_email")
    keyboard.button(text="Проверка номера", callback_data="check_phone")
    keyboard.button(text="Пополнить баланс", callback_data="top_up")
    keyboard.adjust(2)
    return keyboard.as_markup()

def get_user_data(user_id):
    if user_id not in USERS:
        USERS[user_id] = {"checks": 0, "balance": 0.0}
    return USERS[user_id]

@dp.message(F.text == "/start")
async def start(message: Message):
    user_data = get_user_data(message.from_user.id)
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        f"Твой ID: <code>{message.from_user.id}</code>\n"
        f"Баланс: <b>${user_data['balance']:.2f}</b>\n"
        f"Доступные бесплатные проверки: {MAX_FREE_CHECKS - user_data['checks']}",
        reply_markup=main_menu()
    )

@dp.callback_query(F.data == "check_ip")
async def ask_ip(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите IP-адрес:")
    await state.set_state(Form.waiting_for_ip)
    await callback.answer()

@dp.message(Form.waiting_for_ip)
async def process_ip(message: Message, state: FSMContext):
    user_data = get_user_data(message.from_user.id)
    if user_data["checks"] >= MAX_FREE_CHECKS and user_data["balance"] < 0.1:
        await message.answer("Вы исчерпали лимит бесплатных проверок и недостаточно средств на балансе.")
        return

    ip = message.text.strip()
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://ipgeolocation.abstractapi.com/v1/?api_key=76599f16ac4f4a359808485a87a8f3bd&ip_address={ip}") as resp:
            data = await resp.json()

    if "error" in data:
        await message.answer("Ошибка при проверке IP. Убедитесь в правильности ввода.")
    else:
        score = int(data.get('security', {}).get('threat_score', 0))
        color = "🟢"
        if score >= 70:
            color = "🔴"
        elif score >= 40:
            color = "🟡"

        result = (
            f"<b>IP:</b> {data.get('ip')}\n"
            f"<b>Страна:</b> {data.get('country')}\n"
            f"<b>Регион:</b> {data.get('region')}\n"
            f"<b>Город:</b> {data.get('city')}\n"
            f"<b>ZIP-код:</b> {data.get('postal_code')}\n"
            f"<b>Провайдер:</b> {data.get('connection', {}).get('isp')}\n"
            f"<b>Тип соединения:</b> {data.get('connection', {}).get('connection_type')}\n"
            f"<b>VPN:</b> {data.get('security', {}).get('is_vpn')}\n"
            f"<b>Прокси:</b> {data.get('security', {}).get('is_proxy')}\n"
            f"<b>Открытые порты:</b> {', '.join(map(str, data.get('open_ports', [])))}\n"
            f"<b>Черные списки:</b> {', '.join(data.get('blacklists', {}).get('engines', [])) if data.get('blacklists', {}).get('is_blacklisted') else 'Нет'}\n"
            f"<b>Риск:</b> {color} {score}/100"
        )
        await message.answer(result)

        if user_data["checks"] < MAX_FREE_CHECKS:
            user_data["checks"] += 1
        else:
            user_data["balance"] -= 0.10

    await state.clear()

@dp.callback_query(F.data == "check_email")
async def ask_email(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите email:")
    await state.set_state(Form.waiting_for_email)
    await callback.answer()

@dp.message(Form.waiting_for_email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    user_data = get_user_data(message.from_user.id)

    if user_data["checks"] >= MAX_FREE_CHECKS and user_data["balance"] < 0.1:
        await message.answer("Вы исчерпали лимит бесплатных проверок и недостаточно средств на балансе.")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://emailvalidation.abstractapi.com/v1/?api_key=76599f16ac4f4a359808485a87a8f3bd&email={email}") as resp:
            data = await resp.json()

    score = float(data.get('quality_score', 0))
    color = "🟢"
    if score >= 0.7:
        color = "🔴"
    elif score >= 0.4:
        color = "🟡"

    result = (
        f"<b>Email:</b> {email}\n"
        f"<b>Валидный:</b> {data.get('is_valid_format', {}).get('value')}\n"
        f"<b>Существующий домен:</b> {data.get('is_smtp_valid', False)}\n"
        f"<b>Риск:</b> {color} {int(score * 100)}/100"
    )
    await message.answer(result)

    if user_data["checks"] < MAX_FREE_CHECKS:
        user_data["checks"] += 1
    else:
        user_data["balance"] -= 0.10

    await state.clear()

@dp.callback_query(F.data == "check_phone")
async def ask_phone(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите номер телефона в международном формате (например, +79991234567):")
    await state.set_state(Form.waiting_for_phone)
    await callback.answer()

@dp.message(Form.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    user_data = get_user_data(message.from_user.id)

    if user_data["checks"] >= MAX_FREE_CHECKS and user_data["balance"] < 0.1:
        await message.answer("Вы исчерпали лимит бесплатных проверок и недостаточно средств на балансе.")
        return

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://phonevalidation.abstractapi.com/v1/?api_key=76599f16ac4f4a359808485a87a8f3bd&phone={phone}") as resp:
            data = await resp.json()

    risk = data.get('risk', 'unknown')
    score = {"low": 20, "medium": 50, "high": 90}.get(risk, 0)
    color = "🟢"
    if score >= 70:
        color = "🔴"
    elif score >= 40:
        color = "🟡"

    result = (
        f"<b>Номер:</b> {phone}\n"
        f"<b>Страна:</b> {data.get('country')}\n"
        f"<b>Оператор:</b> {data.get('carrier')}\n"
        f"<b>Тип:</b> {data.get('line_type')}\n"
        f"<b>Формат:</b> {data.get('format', {}).get('international')}\n"
        f"<b>Риск:</b> {color} {score}/100"
    )
    await message.answer(result)

    if user_data["checks"] < MAX_FREE_CHECKS:
        user_data["checks"] += 1
    else:
        user_data["balance"] -= 0.10

    await state.clear()

@dp.callback_query(F.data == "top_up")
async def top_up_menu(callback: CallbackQuery):
    kb = InlineKeyboardBuilder()
    kb.button(text="BTC", callback_data="btc")
    kb.button(text="LTC", callback_data="ltc")
    kb.adjust(2)
    await callback.message.answer("Выберите способ пополнения:", reply_markup=kb.as_markup())
    await callback.answer()

@dp.callback_query(F.data == "btc")
async def btc_address(callback: CallbackQuery):
    await callback.message.answer(f"Пополните баланс на адрес BTC:\n<code>{BTC_ADDRESS}</code>")
    await callback.answer()

@dp.callback_query(F.data == "ltc")
async def ltc_address(callback: CallbackQuery):
    await callback.message.answer(f"Пополните баланс на адрес LTC:\n<code>{LTC_ADDRESS}</code>")
    await callback.answer()

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
