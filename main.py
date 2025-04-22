import aiohttp

@router.message(CheckState.ip)
async def process_ip(message: Message, state: FSMContext):
    ip = message.text.strip()

    api_key = "76599f16ac4f4a359808485a87a8f3bd"
    url = f"https://ipgeolocation.abstractapi.com/v1/?api_key={api_key}&ip_address={ip}"

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

    # Цветовая индикация
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
