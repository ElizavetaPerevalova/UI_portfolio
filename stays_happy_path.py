import re

from playwright.sync_api import Page, expect


def test_stays_booking(auth_page: Page):
    auth_page.goto("https://phptravels.net", wait_until="domcontentloaded")
    print("[START] URL after 1st goto:", auth_page.url)

    #  DEMO-MODAL click
    demo_modal = auth_page.locator("#demoWarningModal")
    if demo_modal.is_visible(timeout=3000):
        print("[FIX] Demo-modal is visible")
        demo_modal.get_by_role("button").first.click()
        print("[FIX] Demo-modal is closed")
    else:
        print("[FIX] No Demo-modal")

    # stays page
    print("[INFO] Clicking Stays tab...")
    auth_page.wait_for_load_state("networkidle")
    auth_page.wait_for_timeout(2000)
    auth_page.get_by_role("tab", name="hotel Stays").dispatch_event("click")
    print("[INFO] Waiting for the Stays form to load...")

    # --- Destination ---
    auth_page.locator("#st_dest_trigger").click()
    auth_page.locator("#st_dest_q").fill("New York")
    auth_page.wait_for_timeout(1000)  # Ждем выпадашку

    # 1. Находим сам бейджик "City" (он есть только у нужной нам строки)
    city_badge = auth_page.locator("span:text-is('City'):visible").first

    # 2. Поднимаемся до кликабельного родителя (div с классом cursor-pointer) и кликаем
    city_badge.locator("xpath=ancestor::div[contains(@class, 'cursor-pointer')][1]").click(force=True)

    print("[STEP] Destination selected: New York City")

    auth_page.wait_for_timeout(500)

    # --- Nationality ---
    auth_page.locator("#st_nat_trigger").click()
    auth_page.locator("#st_nat_q").fill("Russia")
    auth_page.wait_for_timeout(1000)  # Ждем выпадашку стран

    # Ищем кликабельную строку с Россией
    ru_option = auth_page.locator("div.cursor-pointer").filter(has_text="Russia").first
    ru_option.click(force=True)
    print("[STEP] Nationality selected: Russia")

    auth_page.wait_for_timeout(500)

    # --- Search ---
    print("[INFO] Clicking Search...")
    auth_page.get_by_role("button", name="Search").click()

    print("[PAUSE] Test finished! Browser will stay open for 5 minutes so you can inspect it.")

    auth_page.wait_for_url("**/stays/**", timeout=30000)
    print("\n[AFTER SEARCH] URL:", auth_page.url)

    # waiting for the results
    results_marker = auth_page.get_by_text(
        re.compile("stays found")
    )
    results_marker.wait_for(state="visible", timeout=60000)
    print("[INFO] Results are ready:", results_marker.inner_text())
    # auth_page.locator("select[x-model='sortBy']").select_option("price_low")
    # auth_page.get_by_text("More details").first.click()

    with auth_page.context.expect_page() as new_page_info:
        auth_page.get_by_text("More details").first.click()

    # Получаем эту новую вкладку
    hotel_page = new_page_info.value

    # Ждем, пока она прогрузится
    hotel_page.wait_for_load_state("domcontentloaded")
    print(f"[SUCCESS] Switched to new tab: {hotel_page.url}")
    # select an option
    hotel_page.locator("span:text-is('Select'):visible").first.click()




    hotel_page.locator("span:text-is('Continue Booking'):visible").first.click()


    hotel_page.wait_for_load_state("domcontentloaded")

    # 1. Выбираем титул (используем тег select и атрибут x-model)
    hotel_page.locator("select[x-model='formData.travelers.room_0.adult_1.title']").select_option("Ms")

    # 2. Заполняем имя (используем тег input и сохраняем в новую переменную!)
    first_name_input = hotel_page.locator("input[x-model='formData.travelers.room_0.adult_1.first_name']")
    first_name_input.fill("Jane")

    # 3. Заполняем фамилию
    last_name_input = hotel_page.locator("input[x-model='formData.travelers.room_0.adult_1.last_name']")
    last_name_input.fill("Doe")
    hotel_page.locator("label[for='payment_3']").click()

    # 1. Сначала НАХОДИМ элемент и сохраняем в переменную (без .click() в конце!)
    hotel_page.locator("#terms_accepted + .checkbox-custom").click()


    hotel_page.get_by_role("button", name="Confirm Booking").click()

    hotel_page.wait_for_url("**/invoice/**", timeout=400000)


    # Проверяем статусы
    expect(hotel_page.get_by_text("Booking Received")).to_be_visible()
    # expect(hotel_page.get_by_text("Invoice")).to_be_visible()


    # Вытаскиваем номер инвойса для лога
    invoice_text = hotel_page.locator("text=/Invoice #[A-Z0-9]+/").first.inner_text()
    print(f"[SUCCESS] Hotel booked successfully! {invoice_text}")
    hotel_page.wait_for_timeout(1000*60*5)