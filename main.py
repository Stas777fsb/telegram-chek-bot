import logging
import re
import sqlite3
import aiohttp
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import CommandStart, Text
import asyncio
from datetime import datetime

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token="7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU", parse_mode=ParseMode.HTML)  # Замени на реальный токен
dp = Dispatcher(storage=MemoryStorage())  # Можно заменить на Redis или другую FSM-хранилку
router = Router()
dp.include_router(router)

# Подключение к SQLite
def init_db():
    conn = sqlite3.connect("bot_history.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS checks
                 (user_id INTEGER, check_type TEXT, value TEXT, result TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

# Сохранение результата в БД
def save_to_db(user_id, check_type, value, result):
    conn = sqlite3.connect("bot_history.db")
    c = conn.cursor()
    c.execute("INSERT INTO checks VALUES (?, ?, ?, ?, ?)",
              (user_id, check_type, value, result, datetime.now().isoformat()))
    conn.commit()
    conn.close()

# FSM состояния
class CheckState(StatesGroup):
    ip = State()
    email = State()
    phone = State()

# Главное меню
def get_main_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Проверка IP")],
            [KeyboardButton(text="Проверка email")],
            [KeyboardButton(text="Проверка номера телефона")],
            [KeyboardButton(text="История проверок")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

# Клавиатура отмены
def get_cancel_keyboard():
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Отмена")]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return kb

# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    init_db()  # Инициализация БД при старте
    await message.answer(
        f"Привет, {message.from_user.first_name}! Выбери нужную проверку:",
        reply_markup=get_main_keyboard()
    )

# Обработка выбора IP-проверки
@router.message(Text("Проверка IP"))
async def check_ip_prompt(message: Message, state: FSMContext):
    await state.set_state(CheckState.ip)
    await message.answer("Введи IP-адрес (например, 8.8.8.8):", reply_markup=get_cancel_keyboard())

# Обработка выбора email-проверки
@router.message(Text("Проверка email"))
async def check_email_prompt(message: Message, state: FSMContext):
    await state.set_state(CheckState.email)
    await message.answer("Введи email (например, example@domain.com):", reply_markup=get_cancel_keyboard())

# Обработка выбора проверки телефона
@router.message(Text("Проверка номера телефона"))
async def check_phone_prompt(message: Message, state: FSMContext):
    await state.set_state(CheckState.phone)
    await message.answer(
        "Введи номер телефона с кодом страны (например, +79876543210):",
        reply_markup=get_cancel_keyboard()
    )

# Обработка истории проверок
@router.message(Text("История проверок"))
async def show_history(message: Message):
    conn = sqlite3.connect("bot_history.db")
    c = conn.cursor()
    c.execute("SELECT check_type, value, result, timestamp FROM checks WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5",
              (message.from_user.id,))
    history = c.fetchall()
    conn.close()

    if not history:
        await message.answer("История проверок пуста.", reply_markup=get_main_keyboard())
        return

    response = "Последние 5 проверок:\n"
    for check_type, value, result, timestamp in history:
        response += f"{check_type}: {value} — {result} ({timestamp})\n"
    await message.answer(response, reply_markup=get_main_keyboard())

# Обработка команды "Отмена"
@router.message(Text("Отмена"), CheckState())
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено. Выбери проверку:", reply_markup=get_main_keyboard())

# Регулярные выражения для валидации
IP_REGEX = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PHONE_REGEX = r"^\+[1-9]\d{9,14}$"

# Проверка IP через API
async def check_ip(ip: str) -> str:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(f"http://ip-api.com/json/{ip}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data["status"] == "success":
                        return f"IP: {ip}\nСтрана: {data['country']}\nГород: {data['city']}\nISP: {data['isp']}"
                    return "IP-адрес не найден."
                return "Ошибка API."
        except Exception as e:
            logger.error(f"Ошибка проверки IP: {e}")
            return "Ошибка при проверке IP."

# Обработка введённого IP
@router.message(CheckState.ip)
async def process_ip(message: Message, state: FSMContext):
    ip = message.text.strip()
    if not re.match(IP_REGEX, ip):
        await message.answer("Некорректный IP-адрес. Попробуй снова:", reply_markup=get_cancel_keyboard())
        return

    result = await check_ip(ip)
    save_to_db(message.from_user.id, "IP", ip, result)
    await message.answer(result, reply_markup=get_main_keyboard())
    await state.clear()

# Обработка введённого email
@router.message(CheckState.email)
async def process_email(message: Message, state: FSMContext):
    email = message.text.strip()
    if not re.match(EMAIL_REGEX, email):
        await message.answer("Некорректный email. Попробуй снова:", reply_markup=get_cancel_keyboard())
        return

    result = f"Email {email} выглядит корректным (валидация прошла)."
    save_to_db(message.from_user.id, "Email", email, result)
    await message.answer(result, reply_markup=get_main_keyboard())
    await state.clear()

# Обработка введённого телефона
@router.message(CheckState.phone)
async def process_phone(message: Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(PHONE_REGEX, phone):
        await message.answer("Некорректный номер телефона. Попробуй снова:", reply_markup=get_cancel_keyboard())
        return

    result = f"Номер {phone} выглядит корректным (валидация прошла)."
    save_to_db(message.from_user.id, "Phone", phone, result)
    await message.answer(result, reply_markup=get_main_keyboard())
    await state.clear()

# Запуск бота
async def main():
    logger.info("Бот запущен")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
