import asyncio import logging import requests from aiogram import Bot, Dispatcher, F from aiogram.types import Message from aiogram.enums import ParseMode from aiogram.fsm.context import FSMContext from aiogram.fsm.state import StatesGroup, State from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from aiogram.fsm.storage.memory import MemoryStorage

API_TOKEN = "7797606083:AAESciBzaFUiMmWiuqoOM61Ef7I7vEXNkQU" IPQUALITY_API_KEY = "QUn48qWULMrgLKONUVMDJ3nG8A7"

logging.basicConfig(level=logging.INFO) bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML) dp = Dispatcher(storage=MemoryStorage())

class CheckState(StatesGroup): waiting_for_input = State() check_type = State()

main_kb = ReplyKeyboardMarkup( keyboard=[ [KeyboardButton(text="Проверка IP")], [KeyboardButton(text="Проверка Email")], [KeyboardButton(text="Проверка номера телефона")] ], resize_keyboard=True )

@dp.message(F.text == "/start") async def cmd_start(message: Message, state: FSMContext): await message.answer("Выберите, что хотите проверить:", reply_markup=main_kb) await state.set_state(CheckState.check_type)

@dp.message(CheckState.check_type) async def handle_check_choice(message: Message, state: FSMContext): text = message.text.lower() if "ip" in text: await message.answer("Введите IP-адрес:") await state.update_data(type="ip") elif "email" in text: await message.answer("Введите Email:") await state.update_data(type="email") elif "телефон" in text: await message.answer("Введите номер телефона:") await state.update_data(type="phone") else: await message.answer("Выберите вариант из меню.") return await state.set_state(CheckState.waiting_for_input)

@dp.message(CheckState.waiting_for_input) async def handle_input(message: Message, state: FSMContext): data = await state.get_data() check_type = data.get("type") input_value = message.text.strip()

if check_type == "ip":
    response = requests.get(
        f"https://ipqualityscore.com/api/json/ip/{IPQUALITY_API_KEY}/{input_value}"
    )
    result = response.json()
    if "error" in result:
        await message.answer("Ошибка: Неверный IP или лимит исчерпан.")
    else:
        risk = int(result.get("fraud_score", 0))
        color = "\U0001F7E2" if risk <= 30 else ("\U0001F7E1" if risk <= 70 else "\U0001F534")
        await message.answer(f"{color} <b>IP:</b> {input_value}\n<b>Риск:</b> {risk}/100\n<b>Страна:</b> {result.get('country_code')}\n<b>Город:</b> {result.get('city')}\n<b>Почтовый индекс:</b> {result.get('zipcode')}\n<b>Прокси/VPN:</b> {'Да' if result.get('proxy') else 'Нет'}")

elif check_type == "email":
    response = requests.get(
        f"https://ipqualityscore.com/api/json/email/{IPQUALITY_API_KEY}/{input_value}"
    )
    result = response.json()
    if "error" in result:
        await message.answer("Ошибка: Неверный email или лимит исчерпан.")
    else:
        risk = int(result.get("fraud_score", 0))
        color = "\U0001F7E2" if risk <= 30 else ("\U0001F7E1" if risk <= 70 else "\U0001F534")
        await message.answer(f"{color} <b>Email:</b> {input_value}\n<b>Риск:</b> {risk}/100\n<b>Был ли взломан:</b> {'Да' if result.get('leaked') else 'Нет'}\n<b>Disposable:</b> {'Да' if result.get('disposable') else 'Нет'}")

elif check_type == "phone":
    response = requests.get(
        f"https://ipqualityscore.com/api/json/phone/{IPQUALITY_API_KEY}/{input_value}"
    )
    result = response.json()
    if "error" in result:
        await message.answer("Ошибка: Номер телефона не найден или лимит исчерпан.")
    else:
        risk = int(result.get("fraud_score", 0))
        color = "\U0001F7E2" if risk <= 30 else ("\U0001F7E1" if risk <= 70 else "\U0001F534")
        await message.answer(f"{color} <b>Телефон:</b> {input_value}\n<b>Риск:</b> {risk}/100\n<b>Страна:</b> {result.get('country_code')}\n<b>Оператор:</b> {result.get('carrier')}\n<b>Тип:</b> {result.get('line_type')}\n<b>Мобильный:</b> {'Да' if result.get('mobile') else 'Нет'}")

await state.clear()
await message.answer("Выберите новое действие:", reply_markup=main_kb)

async def main(): await dp.start_polling(bot)

if name == 'main': asyncio.run(main())
