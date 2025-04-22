import asyncio import aiohttp from aiogram import Bot, Dispatcher, F, Router, types from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton from aiogram.enums import ParseMode from aiogram.fsm.context import FSMContext from aiogram.fsm.state import StatesGroup, State from aiogram.fsm.storage.memory import MemoryStorage from aiogram.filters import Command

bot = Bot(token="7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU", parse_mode=ParseMode.HTML) dp = Dispatcher(storage=MemoryStorage()) router = Router()

class CheckState(StatesGroup): ip = State() email = State() phone = State()

Главное меню

main_kb = ReplyKeyboardMarkup( keyboard=[ [KeyboardButton(text="Проверка IP")], [KeyboardButton(text="Проверка Email")], [KeyboardButton(text="Проверка номера телефона")] ], resize_keyboard=True )

@router.message(Command("start")) async def start_cmd(message: Message): await message.answer("Привет! Я бот для проверки IP, email и телефона.", reply_markup=main_kb)

Обработка кнопок меню

@router.message(F.text == "Проверка IP") async def check_ip(message: Message, state: FSMContext): await message.answer("Введите IP-адрес для проверки:") await state.set_state(CheckState.ip)

@router.message(F.text == "Проверка Email") async def check_email(message: Message, state: FSMContext): await message.answer("Введите email для проверки:") await state.set_state(CheckState.email)

@router.message(F.text == "Проверка номера телефона") async def check_phone(message: Message, state: FSMContext): await message.answer("Введите номер телефона для проверки:") await state.set_state(CheckState.phone)

Проверка IP через Abstract API

@router.message(CheckState.ip) async def process_ip(message: Message, state: FSMContext): ip = message.text.strip() api_key = "76599f16ac4f4a359808485a87a8f3bd" url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={api_key}&ip_address={ip}"

async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        if resp.status != 200:
            await message.answer("Ошибка при запросе данных. Попробуй позже.")
            await state.clear()
            return
        data = await resp.json()

country = data.get("country", "N/A")
region = data.get("region", "N/A")
city = data.get("city", "N/A")
postal = data.get("postal_code", "N/A")
isp = data.get("connection", {}).get("isp_name", "N/A")
is_vpn = data.get("security", {}).get("is_vpn", False)
is_proxy = data.get("security", {}).get("is_proxy", False)
is_tor = data.get("security", {}).get("is_tor", False)
blacklist = data.get("security", {}).get("is_blacklisted", False)

risk_score = 0
if is_vpn: risk_score += 30
if is_proxy: risk_score += 30
if is_tor: risk_score += 40
if blacklist: risk_score += 20
if risk_score > 100: risk_score = 100

if risk_score < 30:
    color = "🟢 Низкий риск"
elif risk_score < 70:
    color = "🟡 Средний риск"
else:
    color = "🔴 Высокий риск"

result = (
    f"<b>Результат проверки IP</b>:\n"
    f"<b>IP:</b> {ip}\n"
    f"<b>Страна:</b> {country}\n"
    f"<b>Регион:</b> {region}\n"
    f"<b>Город:</b> {city}, {postal}\n"
    f"<b>Провайдер:</b> {isp}\n"
    f"<b>VPN:</b> {'Да' if is_vpn else 'Нет'}\n"
    f"<b>Прокси:</b> {'Да' if is_proxy else 'Нет'}\n"
    f"<b>TOR:</b> {'Да' if is_tor else 'Нет'}\n"
    f"<b>В черном списке:</b> {'Да' if blacklist else 'Нет'}\n"
    f"<b>Оценка риска:</b> {risk_score}/100\n"
    f"{color}"
)
await message.answer(result)
await state.clear()

Проверка Email

@router.message(CheckState.email) async def process_email(message: Message, state: FSMContext): email = message.text.strip() api_key = "76599f16ac4f4a359808485a87a8f3bd" url = f"https://emailvalidation.abstractapi.com/v1/?api_key={api_key}&email={email}"

async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        if resp.status != 200:
            await message.answer("Ошибка при проверке email.")
            await state.clear()
            return
        data = await resp.json()

is_valid = data.get("is_valid_format", {}).get("value", False)
is_disposable = data.get("is_disposable_email", {}).get("value", False)
is_blacklisted = data.get("is_blacklisted", {}).get("value", False)
quality_score = data.get("quality_score", "0")

risk = float(quality_score)
if risk >= 0.8:
    color = "🟢 Надежный email"
elif risk >= 0.5:
    color = "🟡 Средний риск"
else:
    color = "🔴 Высокий риск"

result = (
    f"<b>Результат проверки Email</b>:\n"
    f"<b>Email:</b> {email}\n"
    f"<b>Формат:</b> {'Корректный' if is_valid else 'Некорректный'}\n"
    f"<b>Временный:</b> {'Да' if is_disposable else 'Нет'}\n"
    f"<b>В черных списках:</b> {'Да' if is_blacklisted else 'Нет'}\n"
    f"<b>Оценка качества:</b> {quality_score}\n"
    f"{color}"
)
await message.answer(result)
await state.clear()

Проверка номера телефона

@router.message(CheckState.phone) async def process_phone(message: Message, state: FSMContext): phone = message.text.strip() api_key = "76599f16ac4f4a359808485a87a8f3bd" url = f"https://phonevalidation.abstractapi.com/v1/?api_key={api_key}&phone={phone}"

async with aiohttp.ClientSession() as session:
    async with session.get(url) as resp:
        if resp.status != 200:
            await message.answer("Ошибка при проверке номера телефона.")
            await state.clear()
            return
        data = await resp.json()

valid = data.get("valid", False)
country = data.get("country", "N/A")
location = data.get("location", "N/A")
type_ = data.get("type", "N/A")
carrier = data.get("carrier", "N/A")

result = (
    f"<b>Результат проверки телефона</b>:\n"
    f"<b>Телефон:</b> {phone}\n"
    f"<b>Действителен:</b> {'Да' if valid else 'Нет'}\n"
    f"<b>Страна:</b> {country}\n"
    f"<b>Город:</b> {location}\n"
    f"<b>Тип:</b> {type_}\n"
    f"<b>Оператор:</b> {carrier}"
)
await message.answer(result)
await state.clear()

async def main(): dp.include_router(router) await dp.start_polling(bot)

if name == "main": asyncio.run(main())
