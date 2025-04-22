import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command, CommandStart
import asyncio

BOT_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU"
ABSTRACT_API_KEY = "76599f16ac4f4a359808485a87a8f3bd"

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=MemoryStorage())

class CheckIP(StatesGroup):
    waiting_for_ip = State()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Отправь /check_ip чтобы проверить IP-адрес.")

@dp.message(Command("check_ip"))
async def check_ip(message: types.Message, state: FSMContext):
    await message.answer("Введите IP-адрес для проверки:")
    await state.set_state(CheckIP.waiting_for_ip)

@dp.message(CheckIP.waiting_for_ip)
async def process_ip(message: types.Message, state: FSMContext):
    ip = message.text.strip()
    await state.clear()

    try:
        response = requests.get(
            f"https://ipgeolocation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&ip_address={ip}"
        )
        data = response.json()

        # Отладка
        await message.answer(f"<b>DEBUG:</b>\n<code>{str(data)[:4000]}</code>")

        # Защита от отсутствующих полей
        security = data.get('security') or {}
        blacklists = data.get('blacklists') or {}
        open_ports = data.get('open_ports') or []

        score = int(security.get('threat_score') or 0)

        if score < 30:
            risk_color = "🟢"
        elif score < 70:
            risk_color = "🟡"
        else:
            risk_color = "🔴"

        result = (
            f"<b>IP:</b> {data.get('ip_address', 'Неизвестно')}\n"
            f"<b>Страна:</b> {data.get('country', '—')}\n"
            f"<b>Регион:</b> {data.get('region', '—')}\n"
            f"<b>Город:</b> {data.get('city', '—')}\n"
            f"<b>ZIP:</b> {data.get('postal_code', '—')}\n"
            f"<b>Провайдер:</b> {data.get('connection', {}).get('isp_name', '—')}\n"
            f"<b>VPN/Proxy:</b> {'Да' if security.get('is_vpn') or security.get('is_proxy') else 'Нет'}\n"
            f"<b>Открытые порты:</b> {', '.join(map(str, open_ports)) if open_ports else 'Нет данных'}\n"
            f"<b>Черные списки:</b> {', '.join(blacklists.get('engines') or []) if blacklists.get('is_blacklisted') else 'Нет'}\n"
            f"<b>Оценка риска:</b> {risk_color} {score}/100"
        )
        await message.answer(result)

    except Exception as e:
        await message.answer(f"Ошибка при обработке IP: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
