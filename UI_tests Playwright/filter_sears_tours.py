import re

from playwright.sync_api import Page, expect
import re
from playwright.sync_api import Page, expect

def test_stays_booking(logged_in_session, auth_page: Page):
    auth_page.goto("https://phptravels.net", wait_until="domcontentloaded")
    print("[START] URL after 1st goto:", auth_page.url)

    #  DEMO-MODAL click
    # demo_modal = auth_page.locator("#demoWarningModal")
    # if demo_modal.is_visible(timeout=3000):
    #     print("[FIX] Demo-modal is visible")
    #     demo_modal.get_by_role("button").first.click()
    #     print("[FIX] Demo-modal is closed")
    # else:
    #     print("[FIX] No Demo-modal")

    # stays page
    print("[INFO] Clicking Tours tab...")
    auth_page.wait_for_load_state("networkidle")
    auth_page.wait_for_timeout(2000)
    auth_page.get_by_role("tab", name="Tours").dispatch_event("click")
    print("[INFO] Waiting for the tours form to load...")

    # --- Destination ---
    auth_page.locator("#tr_dest_trigger").click()
    auth_page.locator("#tr_dest_q").fill("New york")
    auth_page.wait_for_timeout(1000)
    auth_page.locator("div.cursor-pointer").filter(has_text="New York").first.click()
    auth_page.wait_for_timeout(500)
    auth_page.get_by_role("button", name="Search").click()

    print("[INFO] Searching for tours...")
    print(f"URL: {auth_page.url}")

    print("[INFO] Testing Price Slider via Alpine + noUiSlider...")

    auth_page.evaluate("""() => {
        const sliderEl = document.getElementById('tourPriceSlider');
        if (!sliderEl) return;

        const alpineRoot = sliderEl.closest('[x-data]');
        const data = Alpine.$data(alpineRoot);

        // 1. Обновляем состояние в Alpine.js
        // (Ставим [300, 800], чтобы точно не задеть границы и не сломать логику)
        data.filters.priceRange = [300, 800];

        // 2. Говорим самой библиотеке noUiSlider сдвинуть ползунок
        if (sliderEl.noUiSlider) {
            sliderEl.noUiSlider.set([300, 800]);

            // 3. Принудительно вызываем событие 'change', чтобы Alpine понял, что изменения подтверждены
            sliderEl.noUiSlider.dispatchEvent('change');
        }
    }""")

    # Ждем, чтобы Alpine пересчитал карточки
    auth_page.wait_for_timeout(1500)

    # Проверяем, что ползунок сдвинулся
    lower_handle = auth_page.locator("#tourPriceSlider [data-handle='0']")
    val_text = lower_handle.get_attribute("aria-valuenow")
    final_value = float(val_text) if val_text else 0.0

    print(f"[INFO] Slider value after update: {final_value}")

    # Проверяем, что значение изменилось (а не равно старому 24/28)
    # Мы проверяем, что оно больше 100, чтобы убедиться, что оно сдвинулось вправо
    assert final_value > 100, f"Слайдер не зафиксировался! Значение: {final_value}"

    print("[SUCCESS] Slider moved and stayed!")


    print("[SUCCESS] Test finished!")
    auth_page.pause()