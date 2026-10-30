import re
from playwright.sync_api import Page, expect


def test_passengers_widget(auth_page: Page):
    # adding +1adult, +child, +infant
    auth_page.goto("https://phptravels.net/flights", wait_until="domcontentloaded")

    demo_modal = auth_page.locator("#demoWarningModal")
    if demo_modal.is_visible(timeout=3000):
        print("[FIX] Demo-modal is visible, clicking the button")
        demo_modal.get_by_role("button").first.click()
        print("[FIX] Demo-modal is closed")
    auth_page.wait_for_timeout(500)

    auth_page.get_by_text("1 Passenger").locator("xpath=ancestor::div[contains(@class, 'border')][1]").click()
    auth_page.wait_for_timeout(500)
    print("[FIX] Passengers click")
    auth_page.get_by_role("button", name="add").nth(0).click()
    auth_page.get_by_role("button", name="add").nth(1).click()
    auth_page.get_by_role("button", name="add").nth(2).click()
