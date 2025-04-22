import asyncio import logging from aiogram import Bot, Dispatcher, types, F from aiogram.types import ReplyKeyboardMarkup, KeyboardButton from aiogram.enums import ParseMode from aiohttp import ClientSession from collections import defaultdict import re

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN" IPQUALITY_API_KEY = "YOUR_IPQUALITYSCORE_API_KEY" ABSTRACT_API_KEY = "YOUR_ABSTRACTAPI_KEY" NUMVERIFY_API_KEY = "YOUR_NUMVERIFY_API_KEY"

FREE_LIMIT = 10 PRICE_PER_CHECK = 0.10

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML) dp = Dispatcher()

user_data = defaultdict(lambda: {"free_checks": 0, "balance": 0.0})

menu_keyboard = ReplyKeyboardMarkup( keyboard=[ [KeyboardButton(text="Проверка IP")], [KeyboardButton(text="Проверка номера телефона")], [KeyboardButton(text="Проверка email")], [KeyboardButton(text="Пополнить баланс")] ], resize_keyboard=True )

@dp.message(F.text == "/start") async def start_handler(message: types.Message): user_id = message.from_user.id await message.answer( f"Привет, {message.from_user.first_name}!\n\n" f"Этот бот проверяет IP, телефоны и email на риск.\n" f"Ваш ID: <code>{user_id}</code>\n" f"Баланс: <b>${user_data[user_id]['balance']:.2f}</b>\n" f"Доступно бесплатных IP-проверок: <b>{FREE_LIMIT - user_data[user_id]['free_checks']}</b>", reply_markup=menu_keyboard )

@dp.message(F.text == "Проверка IP") async def ask_ip(message: types.Message): await message.answer("Введите IP-адрес для проверки:")

@dp.message(F.text == "Проверка номера телефона") async def ask_phone(message: types.Message): await message.answer("Введите номер телефона в формате +1234567890:")

@dp.message(F.text == "Проверка email") async def ask_email(message: types.Message): await message.answer("Введите email для проверки:")

@dp.message(F.text == "Пополнить баланс") async def top_up_balance(message: types.Message): keyboard = ReplyKeyboardMarkup( keyboard=[ [KeyboardButton(text="Пополнить BTC")], [KeyboardButton(text="Пополнить LTC")], [KeyboardButton(text="Назад")] ], resize_keyboard=True ) await message.answer("Выберите способ пополнения:", reply_markup=keyboard)

@dp.message(F.text == "Пополнить BTC") async def btc_topup(message: types.Message): await message.answer("Отправьте BTC на адрес:\n<code>19LQnQug2NoWm6bGTx9PWtdKMthHUtcEjF</code>")

@dp.message(F.text == "Пополнить LTC") async def ltc_topup(message: types.Message): await message.answer("Отправьте LTC на адрес:\n<code>ltc1qygzgqj47ygz2qsazquj20u20lffss6dkdn0qk2</code>")

@dp.message(F.text == "Назад") async def back_to_menu(message: types.Message): await message.answer("Вы вернулись в главное меню.", reply_markup=menu_keyboard)

@dp.message() async def universal_handler(message: types.Message): text = message.text.strip() user_id = message.from_user.id

if re.match(r"^\d{1,3}(\.\d{1,3}){3}$", text):
    # IP check
    if user_data[user_id]["free_checks"] < FREE_LIMIT:
        user_data[user_id]["free_checks"] += 1
    elif user_data[user_id]["balance"] >= PRICE_PER_CHECK:
        user_data[user_id]["balance"] -= PRICE_PER_CHECK
    else:
        await message.answer("У вас закончились бесплатные проверки и недостаточно средств.")
        return

    async with ClientSession() as session:
        url = f"https://ipqualityscore.com/api/json/ip/{IPQUALITY_API_KEY}/{text}"
        async with session.get(url) as resp:
            data = await resp.json()

    score = round((1 - data["fraud_score"] / 100) * 100, 2)
    color = "🟢" if score >= 70 else "🟡" if score >= 40 else "🔴"
    blacklist_info = f"{data['bot_status'] + data['proxy'] + data['vpn'] + data['tor']}/50"

    result = (
        f"<b>IP Score: {score} | IP {'Хороший' if score >= 70 else 'Средний' if score >= 40 else 'Плохой'} {color}</b>\n\n"
        f"<b>Подробнее:</b>\n"
        f"Proxy: {'Обнаружен' if data['proxy'] else 'Не обнаружен'}\n"
        f"VPN: {'Обнаружен' if data['vpn'] else 'Не обнаружен'}\n"
        f"АСН: {data.get('asn', '—')}\n"
        f"Провайдер: {data.get('ISP', '—')}\n"
        f"Страна: {data.get('country_name', '—')}\n"
        f"Регион: {data.get('region', '—')}\n"
        f"Город: {data.get('city', '—')}\n"
        f"Индекс: {data.get('zip_code', '—')}\n"
        f"\nЧерный список: {blacklist_info}"
    )
    await message.answer(result)

elif re.match(r"^\+?\d{7,15}$", text):
    # Phone check
    async with ClientSession() as session:
        url = f"http://apilayer.net/api/validate?access_key={NUMVERIFY_API_KEY}&number={text}"
        async with session.get(url) as resp:
            data = await resp.json()

    result = (
        f"<b>Результаты проверки телефона:</b>\n"
        f"Номер: {data.get('international_format', text)}\n"
        f"Страна: {data.get('country_name', '—')}\n"
        f"Оператор: {data.get('carrier', '—')}\n"
        f"Линия: {data.get('line_type', '—')}\n"
        f"Действителен: {'Да' if data.get('valid') else 'Нет'}"
    )
    await message.answer(result)

elif re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", text):
    # Email check
    async with ClientSession() as session:
        url = f"https://emailvalidation.abstractapi.com/v1/?api_key={ABSTRACT_API_KEY}&email={text}"
        async with session.get(url) as resp:
            data = await resp.json()

    result = (
        f"<b>Результаты проверки email:</b>\n"
        f"Email: {data.get('email', text)}\n"
        f"Действителен: {'Да' if data.get('is_valid_format', {}).get('value') else 'Нет'}\n"
        f"MX-запись: {'Да' if data.get('mx_found') else 'Нет'}\n"
        f"SMTP проверка: {'Да' if data.get('smtp_check') else 'Нет'}\n"
        f"Catch-All: {'Да' if data.get('catch_all') else 'Нет'}"
    )
    await message.answer(result)

else:
    await message.answer("Непонятный формат. Введите IP, email или номер телефона.")

if name == "main": logging.basicConfig(level=logging.INFO) asyncio.run(dp.start_polling(bot))
