import re
import requests

BASE_URL = "https://phptravels.net"


def get_csrf_token(session, url):
    """Хелпер для вытаскивания CSRF-токена из HTML"""
    response = session.get(url)
    match = re.search(r'<meta name="csrf-token" content="([^"]+)"', response.text)
    if match:
        return match.group(1)
    return None


def test_full_umrah_booking_e2e():
    """
    Полный E2E API-тест:
    1. Логин
    2. Создание черновика (save-draft) -> получаем booking_hash
    3. Получение CSRF-токена
    4. Подтверждение брони (submit) -> получаем invoice_id
    5. Проверка доступности страницы инвойса
    """
    session = requests.Session()

    # --- ШАГ 1: ЛОГИН ---
    login_url = f"{BASE_URL}/login"
    session.post(login_url, data={"email": "user@phptravels.com", "password": "demouser"})
    print("[INFO] Логин выполнен.")

    # --- ШАГ 2: СОЗДАНИЕ ЧЕРНОВИКА (SAVE-DRAFT) ---
    draft_url = f"{BASE_URL}/api/umrah/booking/save-draft"
    headers_draft = {"accept": "*/*", "content-type": "application/json", "origin": BASE_URL}
    payload_draft = {
        "umrah_id": "10", "umrah_name": "Spiritual Journey to Makkah", "umrah_location": "Makkah",
        "start_date": "02-11-2026", "duration": "7 Nights - 7 Days", "total_adults": 1,
        "total_children": 0, "supplier": "umrah", "currency": "USD", "adult_price": 1200,
        "markup_total_umrah_price": 1200, "slug": "spiritual-journey-to-makkah"
    }

    resp_draft = session.post(draft_url, json=payload_draft, headers=headers_draft)
    assert resp_draft.status_code == 200, f"Ошибка save-draft: {resp_draft.text}"

    draft_json = resp_draft.json()
    booking_hash = draft_json.get("booking_hash") or draft_json.get("hash") or draft_json.get("data", {}).get(
        "booking_hash")

    assert booking_hash, f"Хэш не найден. Ответ: {draft_json}"
    print(f"[INFO] Черновик создан. booking_hash: {booking_hash}")

    # --- ШАГ 3: ПОЛУЧЕНИЕ CSRF-ТОКЕНА ИЗ HTML ---
    booking_page_url = f"{BASE_URL}/umrah/booking/{booking_hash}"
    csrf_token = get_csrf_token(session, booking_page_url)
    assert csrf_token, "Не удалось найти CSRF-токен"
    print(f"[INFO] CSRF-токен получен: {csrf_token[:10]}...")

    # --- ШАГ 4: ПОДТВЕРЖДЕНИЕ БРОНИ (SUBMIT) ---
    submit_url = f"{BASE_URL}/api/umrah/booking/submit"
    headers_submit = {
        "accept": "*/*", "content-type": "application/json", "origin": BASE_URL,
        "referer": booking_page_url, "x-csrf-token": csrf_token
    }
    payload_submit = {
        "csrf_token": csrf_token, "booking_hash": booking_hash,
        "guest_details": {
            "primary_guest": {"title": "Mr", "first_name": "Demo", "last_name": "User", "email": "user@phptravels.com",
                              "phone": "1234567890", "country_code": "01"},
            "booking_for_someone_else": False,
            "travelers": {"room_0": {"adult_1": {"title": "Mr", "first_name": "Demo", "last_name": "User"}}},
            "selected_payment": "7", "special_requests": "", "terms_accepted": True, "booking_type": "logged_in"
        },
        "base_currency": "USD", "display_currency": "USD", "subtotal": 1200, "tax_amount": 0, "final_total": 1200,
        "display_total": 1200, "promo_code": "", "promo_discount": 0
    }

    resp_submit = session.post(submit_url, json=payload_submit, headers=headers_submit)
    assert resp_submit.status_code in [200, 201], f"Ошибка submit: {resp_submit.text}"

    submit_json = resp_submit.json()
    invoice_id = submit_json.get("invoice_id") or submit_json.get("data", {}).get("invoice_id")
    assert invoice_id, f"Сервер не вернул ID инвойса! Ответ: {submit_json}"
    print(f"[SUCCESS] Бронь подтверждена! invoice_id: {invoice_id}")

    # --- ШАГ 5: ПРОВЕРКА СОЗДАННОГО ИНВОЙСА ---
    # Тестирование сторонних платежных API (Stripe/PayPal) не входит в рамки нашего E2E теста.
    # Мы проверяем, что система корректно создала инвойс и он доступен пользователю.
    invoice_page_url = f"{BASE_URL}/invoice/umrah/{invoice_id}"
    print(f"[INFO] Проверяем доступность инвойса: {invoice_page_url}")

    resp_invoice_page = session.get(invoice_page_url)

    assert resp_invoice_page.status_code == 200, f"Не удалось загрузить инвойс: {resp_invoice_page.status_code}"

    # Проверяем, что на странице есть наш номер инвойса и ключевые слова
    page_text_lower = resp_invoice_page.text.lower()
    assert invoice_id in resp_invoice_page.text, "ID инвойса не найден на странице!"
    assert "invoice" in page_text_lower or "payment" in page_text_lower, "Страница не похожа на инвойс!"

    print(f"[SUCCESS] Инвойс {invoice_id} успешно создан и доступен!")
    print("[SUCCESS] Полный E2E API-тест пройден!")