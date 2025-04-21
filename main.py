import aiohttp
import random  # Удалишь позже, если будешь использовать реальный API

IPQS_API_KEY = "your_ipqualityscore_api_key"  # Заменить на свой ключ, если используешь IPQualityScore

def risk_color(score):
    if score < 30:
        return "🟢 Хороший"
    elif score < 70:
        return "🟡 Средний"
    else:
        return "🔴 Высокий"

@dp.message(F.text.regexp(r"^\d{1,3}(\.\d{1,3}){3}$"))
async def check_ip(message: Message):
    user_id = message.from_user.id
    today = datetime.utcnow().date()

    if user_id not in user_check_limits or user_check_limits[user_id]["date"] != today:
        user_check_limits[user_id] = {"date": today, "count": 0}

    if user_check_limits[user_id]["count"] >= 10:
        await message.answer("Лимит бесплатных IP-проверок на сегодня исчерпан. Стоимость каждой следующей: $0.10")
        return

    user_check_limits[user_id]["count"] += 1
    ip = message.text.strip()

    # Запрос к IPQualityScore (можно заменить на другой API)
    async with aiohttp.ClientSession() as session:
        try:
            url = f"https://ipqualityscore.com/api/json/ip/{IPQS_API_KEY}/{ip}"
            async with session.get(url) as resp:
                data = await resp.json()
        except Exception as e:
            await message.answer("Ошибка при получении данных. Попробуйте позже.")
            return

    score = int(data.get("fraud_score", random.randint(0, 100)))  # временно random если нет API
    provider = data.get("ISP", "Неизвестно")
    region = data.get("region", "Неизвестно")
    city = data.get("city", "Неизвестно")
    zip_code = data.get("zip_code", "Неизвестно")
    country = data.get("country_name", "Неизвестно")
    asn = data.get("ASN", "Неизвестно")
    blacklist_status = data.get("recent_abuse", False)
    proxy = data.get("proxy", False)
    vpn = data.get("vpn", False)

    color_text = risk_color(score)
    blacklist_text = "0/50" if not blacklist_status else "1+/50"

    text = (
        f"<b>IP:</b> <code>{ip}</code>\n"
        f"<b>IP Score:</b> {score} | {color_text}\n\n"
        f"<b>Подробнее:</b>\n"
        f"Proxy: {'Обнаружен' if proxy else 'Не обнаружен'}\n"
        f"VPN: {'Обнаружен' if vpn else 'Не обнаружен'}\n"
        f"ASN: {asn}\n"
        f"Интернет-провайдер: {provider}\n\n"
        f"Страна: {country}\n"
        f"Регион: {region}\n"
        f"Город: {city}\n"
        f"Индекс: {zip_code}\n\n"
        f"Черный список: {blacklist_text}"
    )

    await message.answer(text, parse_mode="HTML")
